RootPath := $(shell echo %CD%)
WoxVersion = 1.3.524
PluginDirectory = "%LOCALAPPDATA%\Wox\app-${WoxVersion}\Plugins\CloseIn"
BuildDirectory = "${RootPath}\__build"
PluginName = "Wox.Plugin.CloseIn"
BuildTempDirectory = "${BuildDirectory}\${PluginName}"

copy_plugin:
	mkdir ${PluginDirectory}
	mkdir "${PluginDirectory}\Images"
	copy "${RootPath}\Images" "${PluginDirectory}\Images"
	copy "${RootPath}\main.py" "${PluginDirectory}"
	copy "${RootPath}\plugin.json" "${PluginDirectory}"
	@echo Done


zip:
	@echo Preparing tar for version ${version}
	mkdir "${BuildDirectory}"
	mkdir "${BuildTempDirectory}"
	mkdir "${BuildTempDirectory}\Images"
	copy "${RootPath}\Images" "${BuildTempDirectory}\Images"
	copy "${RootPath}\main.py" "${BuildTempDirectory}"
	copy "${RootPath}\plugin.json" "${BuildTempDirectory}"
	tar -caf "Wox.Plugin.CloseIn_v${version}.zip" --directory="${BuildDirectory}" "${PluginName}"
	rmdir /q /s "${BuildDirectory}"
	@echo Done
