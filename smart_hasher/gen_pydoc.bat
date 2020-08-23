SET PD="C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_86\Tools\scripts\pydoc3.py"

:: cd ..\src\smart_hasher

%PD% -w smart_hasher
%PD% -w __init__
%PD% -w cmd_line
%PD% -w hash_calc
%PD% -w hash_storages
%PD% -w util

%PD% -w tests.test_command_line
%PD% -w tests.test_general
%PD% -w tests.test_hash_storages
%PD% -w tests.util_test

move *.html ..\..\doc

:: cd ..\..\doc