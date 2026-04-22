from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="mcp-doctors")

@mcp.tool()
def get_doctors(location: str) -> str:
    """Get doctors from a specific location"""
    if location != "Rome":
        return f"There are no doctors in {location}"
    
    return f"John Doe"

if __name__ == "__main__":
    mcp.run(transport="stdio")

