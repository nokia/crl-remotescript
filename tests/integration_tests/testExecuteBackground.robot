# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets
Library         RemoteScript
Resource        resource.robot

*** Test Case ***
Bg Only
        Execute Background Command In Target      echo "Hello World"
        ${result} =       Wait Background Execution
        Log               ${result}
        Should Be Equal   ${result.status}          0

Bg And Fg
        Execute Background Command In Target          echo "Starting BG"; date; sleep 2; echo "Stopping BG"; date
        ${fg_result}     Execute Command In Target    echo "Foreground inbetween"; date
        ${bg_result}     Wait Background Execution
        Log              ${fg_result}
        Log              ${fg_result.status}
        Log              ${fg_result.stdout}
        Log              ${bg_result}
        Log              ${bg_result.stderr}
        Should Contain   ${bg_result.stdout}          Starting BG
        Should Contain   ${fg_result.stdout}          Foreground inbetween

Four Bg Processes
        Execute Background Command In Target    echo "Starting BG1"; date; sleep 2; echo "Stopping BG1"; date     default     bg_1
        Execute Background Command In Target    echo "Starting BG2"; date; echo "Stopping BG2"; date              default     bg_2
        Execute Background Command In Target    echo "Starting BG3"; date; sleep 2; echo "Stopping BG3"; date     default     bg_3
        Execute Background Command In Target    echo "Starting BG4"; date; sleep 2; echo "Stopping BG4"; date     default     bg_4
        ${fg_result}          Execute Command In Target       echo "FG1"; date
        ${bg_result_1}        Wait Background Execution       bg_1
        ${bg_result_2}        Wait Background Execution       bg_2
        ${bg_result_3}        Wait Background Execution       bg_3
        ${bg_result_4}        Wait Background Execution       bg_4
        Log                   ${fg_result}
        Log                   ${bg_result_1}
        Log                   ${bg_result_2}
        Log                   ${bg_result_3}
        Log                   ${bg_result_4}
        Should Contain        ${fg_result.stdout}             FG1
        Should Contain        ${bg_result_1.stdout}           Stopping BG1
        Should Contain        ${bg_result_2.stdout}           Stopping BG2
        Should Contain        ${bg_result_3.stdout}           Stopping BG3
        Should Contain        ${bg_result_4.stdout}           Stopping BG4

Multitarget
        Set Target      %{RFCLI_TARGET_1.IP}     %{RFCLI_TARGET_1.USER}     %{RFCLI_TARGET_1.PASS}     target2
        Set Target      %{RFCLI_TARGET_1.IP}     %{RFCLI_TARGET_1.USER}     %{RFCLI_TARGET_1.PASS}     target3
        Set Target      %{RFCLI_TARGET_1.IP}     %{RFCLI_TARGET_1.USER}     %{RFCLI_TARGET_1.PASS}     target4
        Set Target      %{RFCLI_TARGET_1.IP}     %{RFCLI_TARGET_1.USER}     %{RFCLI_TARGET_1.PASS}     target5
        Set Target      %{RFCLI_TARGET_1.IP}     %{RFCLI_TARGET_1.USER}     %{RFCLI_TARGET_1.PASS}     target6
        Execute Background Command In Target    echo bg1     default      bg1
        Execute Background Command In Target    echo bg2     target2      bg2
        Execute Background Command In Target    echo bg3     target3      bg3
        Execute Background Command In Target    echo bg4     target4      bg4
        Execute Background Command In Target    echo bg5     target5      bg5
        Execute Background Command In Target    echo bg6     target6      bg6
        ${result_bg1}      Wait Background Execution         bg1
        ${result_bg2}      Wait Background Execution         bg2
        ${result_bg3}      Wait Background Execution         bg3
        ${result_bg4}      Wait Background Execution         bg4
        ${result_bg5}      Wait Background Execution         bg5
        ${result_bg6}      Wait Background Execution         bg6
        Should Be Equal    ${result_bg1.status}              0
        Should Be Equal    ${result_bg2.status}              0
        Should Be Equal    ${result_bg3.status}              0
        Should Be Equal    ${result_bg4.status}              0
        Should Be Equal    ${result_bg5.status}              0
        Should Be Equal    ${result_bg6.status}              0
        Should Contain     ${result_bg1.stdout}              bg1
        Should Contain     ${result_bg2.stdout}              bg2
        Should Contain     ${result_bg3.stdout}              bg3
        Should Contain     ${result_bg4.stdout}              bg4
        Should Contain     ${result_bg5.stdout}              bg5
        Should Contain     ${result_bg6.stdout}              bg6

Bg And Kill
        Set Target Property        default      connection break is error       False
        Execute Background Command In Target                    sleep 911
        Kill Background Execution
        ${result}                  Wait Background Execution    background      5
        Log                        ${result}
        Execute Background Command In Target                    sleep 911
        Sleep                      3
        Kill Background Execution
        ${result}                  Wait Background Execution    background      5
        Set Target Property        default      connection break is error       True
        Log                        ${result}
        ${result}                  Execute Command In Target    ps wwaux | grep -v grep | grep -E "sleep 911$"
        Log                        ${result}
        Should Be Equal            ${result.status}             1
        Should Be Empty            ${result.stdout}
        Should Be Empty            ${result.stderr}

