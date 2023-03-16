#!/usr/bin/env pwsh
switch ($args[0])
{
  'start'
  {
    Start-VM -Name xMDAw1C9SEpCT1NTS25vd2xlZGdlQVBJcw
  }
  'stop'
  {
    Stop-VM -Name xMDAw1C9SEpCT1NTS25vd2xlZGdlQVBJcw
  }
  default
  {
    Get-VM
  }
}
