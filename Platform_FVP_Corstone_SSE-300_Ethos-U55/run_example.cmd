@echo off
"C:\Program Files\ARM\VHT\models\Win64_VC2017\arm_vsi.exe" -V "..\VSI\audio\python" -f fvp_config.txt -a Objects\microspeech.axf --stat --cyclelimit 4000000000 %*
