# Copyright (C) 2019, Nokia

*** Variable ***
${HOST}         %{RFCLI_TARGET_1.IP}
${USER}         %{RFCLI_TARGET_1.USER}
${PASS}         %{RFCLI_TARGET_1.PASS}
${HOST2}        %{RFCLI_TARGET_1.IP}
${USER2}        %{RFCLI_TARGET_1.USER}
${PASS2}        %{RFCLI_TARGET_1.PASS}
${SU_USER}      fsuitestsysadmin
${SU_PASS}      fsuitestsysadmin

*** Keyword ***
Initialize Targets                    Set Target        ${HOST}         ${USER}         ${PASS}         default      ssh/sftp
        Set Target                    ${HOST2}          ${USER2}        ${PASS2}        scptarget       ssh/scp
        Set Target                    ${HOST2}          ${USER2}        ${PASS2}        sftptarget
        Set Default Target Property   login timeout     3

Init Su Target 1                      Set Target        ${HOST}         ${SU_USER}      ${SU_PASS}      default
        Set Target Property           default           su username     ${USER}
        Set Target Property           default           su password     ${PASS}
        Set Target Property           default           login timeout   3

Init Su Target 2                      Set Target        ${HOST}         ${USER}         ${PASS}         default
        Set Target Property           default           su username     ${SU_USER}
        Set Target Property           default           su password     ${SU_PASS}
        Set Target Property           default           login timeout   3

