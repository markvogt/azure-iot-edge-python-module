# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import asyncio
# 2022 11 01 MV: COMMENTED-OUT the 'input' import - NOW BUILT-INTO python!!!
#from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
# 2022 11 01 MV: added following import to get BETTER string of current version of python...
from platform import python_version
# 2022 11 01 MV: tried adding ANOTHER package for parsing PYTHON VERSIONS which are STRINGS like "3.11.7"...
from packaging.version import parse

async def main():
    try:
        # RETRIEVE the current system version as a String...
        str_currentPythonVersion = python_version()
        # PARSE the current Python version into an actual Python Version OBJECT...
        currentPythonVersion = parse(str_currentPythonVersion)
        # PARSE the minimalPythonVersion into an actual Python Version OBJECT...
        minimalPythonVersion = parse("3.5.3")
        # CHECK to see if running a USEABLE version of Python; otherwise raise an exception... 
        if not currentPythonVersion >= minimalPythonVersion:
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )

        # DISPLAY a diagnostic message...    
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        # 2022 11 02 MV: ALERT - this code can ONLY be executed from WTHIN AN AZURE IOT DEVICE !!!
        str_device2_connectionstring = "HostName=iot-2022-VOGTLAND-demo-01.azure-devices.net;DeviceId=PANASONIC-TOUGHBOOK-MEV-02;SharedAccessKey=+RnUVBQkNf8rdENiiQni/bajfYmdUSPVQvakRLeHINA="
        #module_client = IoTHubModuleClient.create_from_edge_environment()
        module_client = IoTHubModuleClient.create_from_connection_string(str_device2_connectionstring)
        # connect the client.
        await module_client.connect()

        # DEFINE behavior for receiving a C2D (Cloud-to-Device) input message on input1...
        async def input1_listener(module_client):
            while True:
                # DISPLAY the incoming C2D data in the console...
                input_message = await module_client.receive_message_on_input("input1")  # blocking call
                print("input_message.data received on input1 = ")
                print(input_message.data)
                print("input_message.custom properties received on input1 =")
                print(input_message.custom_properties)

                # COMPOSE & SEND BACK a "message recieved" message BACK to the IoT Hub...
                print("ECHOING the received message BACK to the IoT Hub...")
                await module_client.send_message_to_output(input_message, "output1")

        # DEFINE behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(10)

        # SCHEDULE a task for a C2D 'Listener'...
        listeners = asyncio.gather(input1_listener(module_client))
        print ( "The sample is now waiting for messages. ")

        # LAUNCH the stdin listener in its own asynchronous (independent) event-listening loop...
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)
        # AWAIT the user to indicate they are done listening for messages because they pressed "Q" or "q"...
        await user_finished

        # Cancel listening
        listeners.cancel()

        # Finally, disconnect
        await module_client.disconnect()

    # HANDLE all exceptions raised through a common exception 'e'...
    except Exception as e:
        print ( "EXCEPTION thrown; e = %s " % e )
        raise

if __name__ == "__main__":
    # LAUNCH an asyncrhonous independent thread which continually runs main()...
    asyncio.run(main())