import os
import sys
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Configure parameters to spawn our server.py script as a subprocess
# We dynamically target the current running python executable to ensure venv compatibility
server_script_path = os.getenv("EHR_SERVER_PATH")
if not server_script_path:
    raise ValueError("EHR_SERVER_PATH environment variable is not defined in the configuration.")

server_params = StdioServerParameters(
    command=sys.executable,  # Uses the exact python.exe from your active venv
    args=[server_script_path],
    env=os.environ.copy()
)

async def query_mcp_ehr(patient_id: str) -> str:
    """
    Connects to the self-hosted EHR MCP server via stdio transport,
    executes the 'get_patient_medical_history' tool, and returns the result string.
    """
    print(f"[MCP CLIENT] Opening secure connection to EHR-Gateway subprocess...")
    
    try:
        # Establish the stdio pipe communication channel
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Initialize an active protocol session over the channel
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                print(f"[MCP CLIENT] Session initialized. Invoking tool over JSON-RPC stream...")
                
                # Execute the specific tool exposed by our FastMCP server
                result = await session.call_tool(
                    name="get_patient_medical_history",
                    arguments={"patient_id": patient_id}
                )
                
                # Extract the text payload from the structured MCP Content block response
                if result.content and len(result.content) > 0:
                    return result.content[0].text
                return "Error: No text data returned from the EHR server."
                
    except Exception as e:
        print(f"[MCP CLIENT ERROR] Failed to communicate with MCP server: {str(e)}")
        return f"Error: EHR Gateway communication failure. Details: {str(e)}"