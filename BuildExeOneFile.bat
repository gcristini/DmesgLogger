#Variables
set FILE_NAME=DmesgFilter
set SOURCES_DIR=Sources\
set BASE_DIR=Build_Onefile\
set OUT_DIR=%BASE_DIR%%FILE_NAME%
set TEMP_DIR=%BASE_DIR%Tmp

#Create executable
pyinstaller  --onefile %SOURCES_DIR%\DmesgFilter.py --name %FILE_NAME% --distpath %OUT_DIR% --workpath %TEMP_DIR%

#Copy configfile into build directory
copy %SOURCES_DIR%\DmesgFilterConfig.json %OUT_DIR%

#Delect .spec file
del %FILE_NAME%.spec