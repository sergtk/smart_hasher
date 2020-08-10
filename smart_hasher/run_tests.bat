:: Ref: https://docs.python.org/3/library/unittest.html#test-discovery
::python -m unittest discover -s tests --verbose 2 

cls
:: Ref: https://stackoverflow.com/questions/52021815/where-visual-studio-install-python
set RUNNER="C:\Program Files (x86)\Microsoft Visual Studio\Shared\Python37_86\python.exe"
%RUNNER% -m unittest discover -s tests
