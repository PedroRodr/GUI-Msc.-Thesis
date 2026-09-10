Initial Setup:

1) Create a python virtual environment
	Use this command: python -m venv *Folder Name*
	Example: python -m venv mwboard_pump_sw

2) Activate virtual environment. (For this case, you must be inside mwboard_pump_sw folder)
	Use this command: Scripts\activate

3) Install the following packages.
	- pip install pyqt5
	- pip install pyqt5designer
	- pip install pyserial
	- pip install pyqtgraph

4) After package installation, you have to find the file designer.exe in order to create your gui.
	File location: \Lib\site-packages\QtDesigner
	Example: mwboard_pump_sw\Lib\site-packages\QtDesigner

5) Find the designer.exe, and make a shortcut to your main folder.

6) If using VScode, you need to choose your interpreter. This will allow you to use VScode to always run your code.
	Go to the bottom right side of VScode, and click to select the interpreter.
	A window will pop-up, and choose the option "Enter interpreter path...".
	Find python.exe file, it's in your main folder.
	Example: mwboard_pump_sw\Scripts\python.exe

Now you have everything set up.

Everytime you change your .ui file, you need recompile it, in order to generate a new .py file.
	Example command: pyuic5 -x gui_gen.ui -o gui_gen.py


Calculate output frequency adf4351:

Fpfd= REFIN × [(1 + D)/(R × (1 + T))] = 26 MHz

D is the RF REFIN doubler bit (0 or 1) = 0
R is the RF reference division factor (1 to 1023) = 1
T is the reference divide-by-2 bit (0 or 1) = 0
REFIN is the reference, which is 26 MHz

RFout = (INT + (FRAC/MOD)) * (Fpfd/ RFdivider)

MOD = REFIN / Fres = 26 MHz / 200 kHz = 130. Fres is the desired resolution.
RFdivider = 1. If lower frequencies are desired, RFdivider much be bigger.
Choose INT and FRAC accordingly to set the desired frequency between  2.2 GHz up to 4.4 GHz.

Power supply settings:

-> MW system with one MW module: 16 V ***  0.5 A
-> Pump Board: 6 V *** 1 A


Problemas comuns:
1) Erro transpose matrix ou falha ao receber os dados, ocorre de forma aleatoria devido a má conexão do cabo. Nessas situações conferir se o cabo de conexão com a probe esta bem soldado