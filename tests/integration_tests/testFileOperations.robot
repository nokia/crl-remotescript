# Copyright (C) 2019, Nokia

*** Setting ***
Test Setup      Initialize Targets And Create Tempdir
Test Teardown   Delete Tempdir
Library         OperatingSystem
Library         RemoteScript
Resource        resource.robot

*** Variable ***
${DIR}          /tmp/pdrobot-remotescript-unittest-%{USER}

*** Test Case ***
Create Directory In Target      Log     See setup and teardown

Copy File To Target SFTP
         Copy To Target

Copy File To Target SCP
         Copy To Target  scptarget

Copy File From Target SFTP
        Copy From Target

Copy File From Target SCP
        Copy From Target        scptarget

Get To Dir SFTP
        Get To Dir

Get To Dir SCP
        Get To Dir              scptarget

Get Named File SFTP
        Get Named File

Get Named File SCP
        Get Named File          scptarget

Copy Directory To Target SFTP
        Copy Dir To Target

Copy Directory To Target SCP
        Copy Dir To Target      scptarget

Copy File Between SFTP Targets
        ${result}               Copy File Between Targets       sftptarget      /bin/bash       default     ${DIR}/t2t
        Should Be Equal         ${result.status}                0
        ${result}               Execute Command In Target       ls ${DIR}/t2t/bash
        Should Be Equal         ${result.status}                0

*** Keyword ***
Initialize Targets And Create Tempdir
        Initialize Targets
        Create Tempdir

Create Tempdir
        Create Directory In Target      ${DIR}
        ${result}                       Execute Command In Target       ls -d ${DIR}
        Should Be Equal                 ${result.status}                0

Delete Tempdir
        ${result}                       Execute Command In Target       rm -rf ${DIR}
        Should Be Equal                 ${result.status}                0

Copy To Target
        [Arguments]                     ${target}=default
        Create File                     local.file                      Hello
        ${result}                       Copy File To Target             local.file      ${DIR}  0755    ${target}
        Should Be Equal                 ${result.status}                0
        ${result}                       Execute Command In Target       ls ${DIR}/local.file    ${target}
        Should Be Equal                 ${result.status}                0

Copy From Target
        [Arguments]                      ${target}=default
        Execute Command In Target       touch ${DIR}/remote.file        ${target}
        ${result}                       Copy File From Target           ${DIR}/remote.file      .       ${target}
        Should Be Equal                 ${result.status}                0
        File Should Exist               ./remote.file

Get To Dir
        [Arguments]                     ${target}=default
        Execute Command In Target       touch ${DIR}/remote.file        ${target}
        Create Directory                to_dir
        ${result}                       Copy File From Target           ${DIR}/remote.file      to_dir  ${target}
        Should Be Equal                 ${result.status}                0
        File Should Exist               ./to_dir/remote.file

Get Named File
        [Arguments]                     ${target}=default
        Execute Command In Target       touch ${DIR}/remote.file        ${target}
        ${result}                       Copy File From Target           ${DIR}/remote.file      renamed.file    ${target}
        Should Be Equal                 ${result.status}                0
        File Should Exist               ./renamed.file

Copy Dir To Target
        [Arguments]             ${target}=default
        Create Directory        a
        Create Directory        a${/}b
        Create Directory        a${/}b${/}c
        Create Directory        a${/}d
        Create File             a${/}a.file                 Hello
        Create File             a${/}b${/}/c${/}c.file      Hello
        ${result}               Copy Directory To Target    a         ${DIR}/a/       0755    ${target}
        Should Be Equal         ${result.status}            0
        ${result}               Execute Command In Target   ls -R ${DIR}    ${target}
        Log                     ${result}
        ${result}               Execute Command In Target   ls ${DIR}/a/a.file      ${target}
        Should Be Equal         ${result.status}            0
        ${result}               Execute Command In Target   ls ${DIR}/a/b/c/c.file  ${target}
        Should Be Equal         ${result.status}            0
        ${result}               Execute Command In Target   ls ${DIR}/a/d   ${target}
        Should Be Equal         ${result.status}            0

