import base64
import os
import uuid
from typing import List
from fastmcp import FastMCP

mcp = FastMCP("Utility MCP Server")
@mcp.tool()
def generate_password()->str:
  """
Generate a pseudo-random password for development use.

This function creates a password by encoding a UUID4 string in base64
and then reversing the resulting string. It's intended for use in
development or testing environments where cryptographic security is not
critical.

Returns:
    str: A reversed base64-encoded UUID4 string, typically around 48 characters.
    May include alphanumeric characters, '+', '/', and '=' padding.

Security Notes:
    - Uses the string form of UUID4 (not raw bytes), so effective entropy is lower (~190 bits of input chars)
    - Suitable for temporary or development credentials.
    - NOT recommended for production use.
    - For higher security, consider using secrets.token_urlsafe().

Example:
    &gt;&gt;&gt; generate_password()
    '==dGM0ZTcwLTI0ZTUtNDJlZC05Y2I1LTk3OGJjODAxMDAwNw=='
"""
  uuid_string = str(uuid.uuid4()).encode()
  base64_encoded = base64.b64encode(uuid_string).decode()
  return base64_encoded[::-1]

@mcp.tool() 
def list_files(directory: str = ".") -> List[str]: 
  """ List all files and directories in a specified path.

  This tool allows the AI to explore the file system by returning a list 
  of names of the entries in the directory given by path.

  Args:
      directory (str): The path to the directory to list. Defaults to the 
      current working directory (".").

  Returns:
      List[str]: A list of filenames and directory names. If an error 
      occurs (e.g., directory not found), returns a list containing 
      the error message.
  """
  try:
    return os.listdir(directory)
  except Exception as e:
    return [f"Error: {str(e)}"]

@mcp.tool(description='Read and return the full text content of a file.') 
def read_file(filename: str) -> str:
  """ 
  Read and return the full text content of a file.

  This tool enables the AI to analyze the contents of specific text files 
  within the accessible file system.

  Args:
      filename (str): The path to the file that needs to be read.

  Returns:
      str: The complete string content of the file encoded in UTF-8. 
      If the file cannot be read, returns an error message starting 
      with "Error reading file:".
  """
  try:
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()
  except Exception as e:
      return f"Error reading file: {str(e)}"

@mcp.resource("data://sys-info", description=" Get a comprehensive system snapshot including time, hardware specs, and real-time health metrics. ") 
def get_system_info() -> str:
  import platform 
  import psutil 
  import subprocess 
  from datetime import datetime

  now = datetime.now()
  timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
  day_name = now.strftime("%A")


  boot_time = datetime.fromtimestamp(psutil.boot_time())
  uptime = str(now - boot_time).split('.')[0]

  sys_type = platform.system()
  machine = platform.machine()
  cpu_count = psutil.cpu_count(logical=False)
  try:
      gpu_info = subprocess.check_output(
          ["nvidia-smi", "--query-gpu=gpu_name", "--format=csv,noheader"], 
          encoding="utf-8"
      ).strip()
  except Exception:
      gpu_info = "N/A (NVIDIA-SMI not found)"

  cpu_usage = psutil.cpu_percent(interval=None)
  memory = psutil.virtual_memory()
  disk = psutil.disk_usage('C:\\')

  return f"""
          --- Hardware Specs ---
          OS:        {sys_type} ({machine})
          CPU:       {cpu_count} Physical Cores
          GPU:       {gpu_info}

          --- Temporal Context ---
          Date/Time: {timestamp}
          Day:       {day_name}
          Uptime:    {uptime}

          --- Resource Utilization ---
          CPU Load:  {cpu_usage}%
          RAM Usage: {memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)
          Disk (C:): {disk.percent}% Used ({disk.free // (1024**3)}GB Free)
          """

@mcp.prompt(description='General purpose prompt for any task with optional context.') 
def helper_prompt(task: str, context: str = "") -> str: 
  base_prompt = f""" Task: {task}
  Please approach this systematically:

  Break down the problem

  Consider multiple solutions

  Explain your reasoning

  Provide clear, actionable steps """

  if context: base_prompt += f"\n\nAdditional context: {context}" 
  return base_prompt

@mcp.prompt()
def api_endpoint_design_prompt(endpoint_name: str, purpose: str) -> str:
  """Specific prompt for designing RESTful API endpoints."""
  return f""" Design a RESTful API endpoint: {endpoint_name} Purpose: {purpose}

  Please provide:

      HTTP method and URL pattern
      Request/response schemas with examples
      Status codes and error handling
      Authentication requirements
      Rate limiting considerations
      OpenAPI/Swagger documentation snippet

  Follow REST conventions and include proper validation. Use JSON for data exchange and meaningful HTTP status codes.
  """

if __name__ == "__main__":
  #mcp.run(transport="streamable-http", host='0.0.0.0', port=8000)
  mcp.run()