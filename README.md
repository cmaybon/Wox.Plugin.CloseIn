# CloseIn
Used to terminate a process/running exe in the future or shutdown your PC.

Example:
`closein discord 1h5m15s`

![Preview](preview.gif)

---
## Development
To use the Makefile be sure to set the `WoxVersion` field in the [MakeFile](Makefile) to your used Wox version.  

Run `make` to copy the plugin to your Wox directory.  
Run `wpm uninstall CloseIn` to uninstall the plugin within Wox. 

Run `make zip version=<number>` to create a `.zip` ready for a Github release. 
