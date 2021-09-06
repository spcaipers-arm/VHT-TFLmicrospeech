#!/usr/bin/env bash
arm_vsi.x -V "../VSI/audio/python" -f fvp_config.txt -a Objects/microspeech.axf --stat --cyclelimit 4000000000 $*
