# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets And Create Tempdir
Test Teardown   Delete Tempdir
Library         OperatingSystem
Library         RemoteScript
Resource        resource.robot

*** Variable ***
${DIR}  /tmp/pdrobot_remotescript_unittest-%{USER}

*** Test Case ***
Create Directory In Target
        Log                      See setup and teardown

Copy File To Target
        Create File              local.file              Hello
        Copy File To Target      local.file              ${DIR}          ftptarget
        ${result}                Execute Command In Target               ls ${DIR}/local.file    target2
        Should Be Equal          ${result.status}        0

Copy File From Target
        Execute Command In Target       touch ${DIR}/remote.file        target2
        Copy File From Target           ${DIR}/remote.file              ftptarget
        File Should Exist               ./remote.file

Get Named File
        Execute Command In Target       touch ${DIR}/remote.file        target2
        Copy File From Target           ${DIR}/remote.file              renamed.file    ftptarget
        File Should Exist               ./renamed.file

Copy Directory To Target
        Create Directory          a
        Create Directory          a${/}b
        Create Directory          a${/}b${/}c
        Create Directory          a${/}d
        Create File               a${/}a.file                 Hello
        Create File               a${/}b${/}/c${/}c.file      Hello
        Copy Directory To Target  a                           ${DIR}/a/                ftptarget
        ${result}                 Execute Command In Target   ls -R ${DIR}             target2
        Log                       ${result}
        ${result}                 Execute Command In Target   ls ${DIR}/a/a.file       target2
        Should Be Equal           ${result.status}            0
        ${result}                 Execute Command In Target   ls ${DIR}/a/b/c/c.file   target2
        Should Be Equal           ${result.status}            0
        ${result}                 Execute Command In Target   ls ${DIR}/a/d            target2
        Should Be Equal           ${result.status}            0


*** Keyword ***
Initialize Targets And Create Tempdir
        Initialize Targets
        Set Target                ${HOST}      ${USER}        ${PASS}       ftptarget       FTP
        Set Target                ${HOST2}     ${USER2}       ${PASS2}      target2         SSH
        Create Tempdir

Create Tempdir
        Create Directory In Target             ${DIR}                       ftptarget
        ${result}                              Execute Command In Target    ls -d ${DIR}    target2
        Should Be Equal                        ${result.status}             0

Delete Tempdir
        ${result}                              Execute Command In Target    rm -rf ${DIR}   target2
        Should Be Equal                        ${result.status}             0
