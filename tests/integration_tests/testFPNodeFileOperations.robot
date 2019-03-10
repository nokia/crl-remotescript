# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets And Create Tempdir
Test Teardown   Delete Tempdir
Library         OperatingSystem
Library         RemoteScript.FP
Resource        resource.robot

*** Variable ***
${DIR}          /tmp/pdrobot-remotescript-unittest-%{USER}
${NODE}         CLA-0

*** Test Case ***
Copy File To Node SFTP
        Copy To Node

Copy File To Node SCP
        Copy To Node        scptarget

Copy File From Node SFTP
        Copy From Node

Copy File From Node SCP
        Copy From Node      scptarget

Get To Dir SFTP
        Get To Dir

Get To Dir SCP
        Get To Dir          scptarget

Get Named File SFTP
        Get Named File

Get Named File SCP
        Get Named File      scptarget

*** Keyword ***
Initialize Targets And Create Tempdir
        Initialize Targets
        Create Tempdir

Create Tempdir
        ${result}           Execute Command In Node ${NODE} mkdir ${DIR}
        Should Be Equal     ${result.status}        0

Delete Tempdi
        ${result}           Execute Command In Node ${NODE} rm -rf ${DIR}
        Should Be Equal     ${result.status}        0

Copy To Node
        [Arguments]         ${target}=default
        Create File         local.file      Hello
        ${result}           Copy File To Node           ${NODE} local.file      ${DIR}  0755    ${target}
        Should Be Equal     ${result.status}            0
        ${result}           Execute Command In Node     ${NODE} ls ${DIR}/local.file    ${target}
        Should Be Equal     ${result.status}            0

Copy From Node
        [Arguments]         ${target}=default
        Execute Command In Node     ${NODE}         touch ${DIR}/remote.file        ${target}
        ${result}           Copy File From Node     ${NODE} ${DIR}/remote.file      .       ${target}
        Should Be Equal     ${result.status}        0
        File Should Exist   ./remote.file

Get To Dir
        [Arguments]         ${target}=default
        Execute Command In Node     ${NODE}         touch ${DIR}/remote.file        ${target}
        Create Directory    to_dir
        ${result}           Copy File From Node     ${NODE} ${DIR}/remote.file      to_dir  ${target}
        Should Be Equal     ${result.status}        0
        File Should Exist   ./to_dir/remote.file

Get Named File
        [Arguments]         ${target}=default
        Execute Command In Node     ${NODE}         touch ${DIR}/remote.file        ${target}
        ${result}           Copy File From Node     ${NODE} ${DIR}/remote.file      renamed.file    ${target}
        Should Be Equal     ${result.status}        0
        File Should Exist   ./renamed.file

