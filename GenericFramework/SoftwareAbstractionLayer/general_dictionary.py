# Global Python Imports
import sys

# Local Python Imports
import lib_constants
sys.path.append(lib_constants.IVE_UTR_FOLDERPATH)
from Source import *

################################################################################
# RE dictionary for grammars
################################################################################
RE_dict = \
    {

        "( *)dummy( +)script( *)":
            code_gen_dummy_script.generate_code_dummy,                          # UDL - 0, RE for dummy script or Not applicable test steps

        "( *)Preload( +)OS(( +)from( +)(\\bNetwork\\b)( +)to( +)())?( *)":
            code_gen_os_preload.generate_code_os_preload,                       # UDL - 1, RE for Preload OS

        "( *)Verify( +)if( +)(.*)( +)of( +)(.*)( +)is( +)(.*)( +)in( +)"
        "device manager( *)":
            code_gen_verify_device_attributes.
            generate_code_verify_device_attributes,                             # UDL - 2, RE For Verify if <property_name> of <device_name> is <expected_value> in device manager

        "( *)Verify( +)(\\bLAN\\b|\\bWIFI\\b|\\bBT\\b|\\bWWAN\\b|\\bWLAN\\b|"
        "\\b3G LTE\\b|\\b4G LTE\\b|\\bGNSS\\b|\\bGPS\\b|\\bWiDi\\b|\\bWiGig\\b)"
        "( +)connectivity( *)":
            code_gen_verify_network_connectivity.
            generate_code_verify_network_connectivity,                          # UDL - 3, RE for Verify <LAN/Wifi/WLAN/WWAN/BT> connectivity

        "( *)verify( +)parse( +)log( +)for( +)(.*)":
            code_gen_parse_log_file.generate_code_parse_log_file,               # UDL - 5, RE For verify parse log for <parameter>{ <delimiter> <expected_value>} from <source>

        "( *)Read( +)SMBIOS( +)Structures( +)for( +)(.*)( *)":
            code_gen_read_smbios_value.generate_code_read_smbios_value,         # UDL - 8, RE for Read SMBIOS structure data
 
        "( *)Read( +)system( +)variable( +)(.*)(( +)from( +)Step( +)([0-9]+)"
        "( +)log)?( *)":
            code_gen_read_system_variable.generate_code_read_system_variable,   # UDL - 9, RE for Read system variable <variable_name> {from Step <step no> log}

        "( *)Verify( +)the( +)postcode( +)Sequence( +)till( +)"
        "(\\bOS\\b|\\bEDK Shell\\b)( +)as( +)per( +)sequence( +)(.*)"
        "(( +)for( +)(\\bFast Boot\\b|\\bFull Boot\\b))?( *)":
            code_gen_read_post_code_sequence.
            generate_code_read_post_code_sequence,                              # UDL - 10, RE for Verify post code sequence

        "( *)Run( +)the( +)command( +)'( *)(.*)( *)'( +)in( +)"
        "(\\befi_shell\\b|\\bpowershell\\b|\\bcommand_prompt\\b)( *)":
            code_gen_run_command.generate_code_run_command,                     # UDL - 11, RE For Run the command <token1> in <Powershell/EFI_shell/command_prompt>

        "( *)Put( +)(\\bSystem\\b)( +)to( +)(\\bS[3-5]\\b|\\bS0i[1-3]\\b|"
        "\\bCMS\\b|\\bDeepS[3-5]\\b)"
        "( +)using( +)(\\bpwr_btn\\b|\\bLID_Action\\b)(( *)$|"
        "(( +)for( +)\\d+( +)second(s*)( *)))":
            code_gen_put_system_to_sx.generate_code_put_system_to_sx,           # UDL - 13, RE for Put <System> to <Sx_state> using <Source> {for <time> seconds}

        "( *)Read( +)and( +)verify( +)ACPI( +)(\\btable\\b|\\bdump\\b)(( +)"
        "(.*))?(( +)(.*))?(( +)for( +)device( +)(.*))?( *)":
            code_gen_verify_acpi_table_variable.
            generate_code_verify_acpi_table,                                    # UDL - 14, RE for verify ACPI <Table/Dump> {Table/Method name} {<Field Name>/bit[<m>:<n>]} {under <method_name> method}{for device <device_name>}

        "( *)Load( +)BIOS( +)defaults( *)":
            code_gen_load_bios_defaults.generate_code_load_bios_defaults,       # UDL - 18, RE for Load bios defaults

        "( *)Boot( +)to( +)(\\bos\\b|\\bedk shell\\b|\\bsetup\\b|"
        "\\bBIOS setup\\b)"
        "(( +)from( +)( *))?( *)":
            code_gen_boot_to_os.generate_code_boot_to_os,                       # UDL - 19, RE For Boot to <Param1> from <Param2>

        "( *)Perform( +)(\\bS[3-5]\\b|\\bS0i[1-3]\\b|\\bCS\\b|\\bMos\\b|"
        "\\bDeepS3\\b|\\bDeepS4\\b|\\bDeepS5\\b|\\bSENTER-SEXIT\\b|\\bCM0\\b|"
        "\\bCMOff\\b|\\bME-PG\\b|\\bGlobal reset\\b|\\bWarm reset\\b|"
        "\\bCold reset\\b|\\bConnected-MOS\\b|\\bDisconnected-MOS\\b)"
        "( +)Cycle(s*)( +)for( +)(\\bConfig-(.*)\\b|\\b([0-9]+)\\b)"
        "( +)time(s*)( *)":
            code_gen_perform_sx_cycles.generate_code_perform_sx_cycles,         # UDL - 20, RE for Perform sx cycles

        "( *)Restart( +)the( +)system( *)":
            code_gen_restart_the_system.generate_code_restart_the_system,       # UDL - 21, RE for restarting the system from BIOS or EDK Shell

        "( *)Perform( +)G3( *)(( +)in( +)(\\bS[3-5]\\b|\\bS0i[1-3]\\b|"
        "\\bDeepS[3-5]\\b))?( *)":
            code_gen_perform_g3.generate_code_perform_g3,                       # UDL - 22, RE for Perform G3

        "( *)Read( +)PCI( +)Register( +)of( +)Bus( +)(\\b0x([a-fA-F0-9]+)\\b|"
        "\\b([a-fA-F0-9]+)h\\b)( +)Device( +)(\\b0x([a-fA-F0-9]+)\\b|"
        "\\b([a-fA-F0-9]+)h\\b)( +)Function( +)(\\b0x([a-fA-F0-9]+)\\b|"
        "\\b([a-fA-F0-9]+)h\\b)( +)offset( +)(\\b0x([a-fA-F0-9]+)\\b|\\b"
        "([a-fA-F0-9]+)h\\b)(.*)":
            code_gen_read_bdf.generate_code_ReadBDF,                            # UDL - 23, RE for Read PCI Register

        "( *)Read( +)MSR( +)?(.*)of( +)address( +)( *)":
            code_gen_read_msr.generate_code_read_msr,                           # UDL - 24, RE for Read MSR{ core <core_num>} of address <address>{ with (bit<bit_position>|bits <bit_positions>|range <start_bit>:<end_bit>)} = <data_value>

        "( *)Write( +)MSR(.*)of( +)address( +)(.*)( +)(.*)=( +)(.*)( *)":
            code_gen_write_msr_config.generate_code_write_msr_config,           # UDL - 25, RE for Write MSR{ core <core_num>} of address <address>{ with (bit<bit_position>|bits <bit_positions>|range <start_bit>:<end_bit>)} = <data_value>

        "( *)Write( +)MMIO( +)register( +)address( +)(.*)( +)offset( +)(.*)"
        "=( +)(.*)( *)":
            code_gen_write_mmio.generate_code_write_mmio,                       # UDL - 26, RE for Write MMIO register address

        "( *)Read( +)bios( +)/bios(.*)(( *)=( *)(.*))?( *)":
            code_gen_read_bios.generate_code_read_bios,                         # UDL - 27, RE for Read BIOS(Bios Path) {<=> <values>}

        "( *)Set( +)bios( +)/bios(.*)( *)=( *)(.*)( *)":
            code_gen_set_bios.generate_code_set_bios,                           # UDL - 28, RE For Set BIOS (Path)<=values>

        "( *)Install( +)(.*)( +)(\\bDriver\\b|\\bPackage\\b)( *)":
            code_gen_install_drivers.generate_code_install_drivers,             # UDL - 29, RE for Install <driver_name> driver {from <driver path>}

        "( *)Uninstall( +)(.*)( +)(\\bDriver\\b|\\bPackage\\b)( *)":
            code_gen_uninstall_drivers.generate_code_uninstall_drivers,         # UDL - 30, RE for Uninstall <driver_name> driver/package

        "( *)Compare( +)if( +)results( +)of( +)Step( +)([0-9]+)( +)(=|<|"
        "contains|>|<=|>=|!=|<>)( +)(.*)(( +)in( +)Host-System)?( *)":
            code_gen_compare_step_results.generate_code_compare_step_results,   # UDL - 32, RE For Compare if results of <Step> <m> <OPERATOR> {Step} <n/Numeric value/String/Config-Tag-variable>

        "( *)Switch( +)from( +)(\\bAC\\b|\\bDC\\b)( +)to( +)(\\bAC Dock\\b|"
        "\\bDC\\b|\\bAC\\b|\\bWireless charging Dock\\b)( *)":
            code_gen_ac_to_dc_switching.code_generate_ac_to_dc_switching,       # UDL - 34, RE for Switch from <AC> to <DC>

        "( *)Check(( +)(.*)( +)in)?( +)device( +)manager( +)for"
        "(( +)any(( +)new)?)?( +)yellow( +)bangs( *)":
            code_gen_verify_yellow_bang.generate_code_verify_yellow_bang,       # UDL - 38, RE for Check {<device name> in} device manager for {any {<new>}} yellow bangs

        "( *)Read( +)MMIO( +)register( +)address( +)(.*)( +)offset( +)(.*)":
            code_gen_read_mmio.generate_code_read_mmio,                         # UDL - 41, RE for Read MMIO register

        "( *)KeyPress( +)(\\btext\\b|\\bspl\\b)( +)( *)=( +)( *)":
            code_gen_press_keys.code_gen_press_keys,                            # UDL - 48, RE for KeyPress <text/spl>="<keys>" {action <hold/release> } { for <#> times}

        "( *)Perform( +)(\\bEnable\\b|\\bDisable\\b)(.*)in( +)"
        "device( +)manager":
            code_gen_enable_disable_devices.
            generate_code_enable_disable_devices,                               # UDL - 50, RE for Enabling/Disabling the devices in device manager

        "( *)Setup( +)(\\bsingle\\b|\\bdual\\b|\\btri\\b|\\bfour\\b)( +)"
        "display(.*)( +)using( +)( *)":
            code_gen_display_configuration_in_os.
            generate_code_display_configuration_in_os,                          # UDL - 372, RE for display configuration

        "( *)Verify( +)(\\bBIOS Setup\\b|\\bUEFI\\b|\\bOS\\b)( +)display( *)":
            code_gen_verify_display.generate_code_verify_display,               # UDL - 374, RE for to verify the display (OS, BIOS, EFI)

        "( *)Capture( +)(.*)( +)using( +)(\\bUF\\b|\\bUSB\\b|\\bUSB2.0\\b|"
        "\\bUSB3.0\\b|\\bWF\\b)( +)camera( +)(.*)( *)":
            code_gen_photo_video_capture_using_camera_in_different_modes.
            generate_code_photo_video_capture_using_camera,                     # UDL - 376, RE for Capture photo/video with different settings

        "( *)Cold-plug( +)(\\bType-C-USB3.1-Pendrive\\b|\\bUSB3.0-Pendrive\\b|"
        "\\bUSB-HUB\\b|\\bUSB-Pendrive\\b|\\bUSB2.0-HUB\\b|\\bUSB2.0-Pendrive"
        "\\b|\\bUSB3.1-SSD\\b|\\bUSB-Keyboard\\b|\\bUSB-Mouse\\b|\\bUSB3.0-HDD"
        "\\b|\\bUSB3.0-HUB\\b|\\bUSB-Ethernet-Dongle\\b|\\bLAN-Cable\\b|"
        "\\bType-C-USB3.1-Gen2-SSD\\b|\\bPS2-keyboard\\b|\\bSensor-Hub\\b|"
        "\\bSerial-Cable\\b|\\bSATA-SSD\\b|\\bedp-display\\b|\\bWIFI_BT_Module"
        "\\b|\\bWIFI-Module\\b|\\bSATA-HDD\\b|\\bISH-Module\\b|\\bDP-Display"
        "\\b|\\bHDMI-Display\\b|\\bCNVI-CRF-MODULE\\b|\\beMMC-Module\\b|"
        "\\bType-C-to-A-dongle\\b|\\bPCIe-NVMe-SSD\\b|\\bCamera-Module\\b|"
        "\\bSerial-to-USB-Cable\\b|\\bIR-CAMERA-MODULE\\b|\\bDead-battery\\b|"
        "\\bType-C-USB3.1-Gen1-SSD\\b|\\bUSB3.0-debug-cable\\b|\\bNVMe-SSD\\b|"
        "\\bFlash-camera-device\\b|\\bSerial-Debug-Cable\\b|\\bUSB-Camera\\b|"
        "\\bIPU-Camera-Module\\b|\\bUSB-Type-C-Power-Adapter\\b)"
        "((( +)from( +)(\\bLAN-Switch\\b|\\bHost-System\\b)( +)to( +)"
        "(\\bSerial\\b|\\bUSB3.0-Type-A\\b|\\bUSB-HUB\\b|\\bUSB2.0-HUB\\b|"
        "\\bUSB-LAN-Adaptor\\b|\\bType-C\\b|\\bM.2-connector\\b|"
        "\\bUSB3.0-debug\\b)( +)port)?)?( *)":
            code_gen_plug_unplug.generate_code_plug_unplug,                     # UDL - 382, RE for cold plug

        "( *)Cold-unplug( +)(\\bUSB3.0-Pendrive\\b|\\bUSB2.0-pendrive\\b|"
        "\\bType-C-to-A-dongle\\b)":
            code_gen_plug_unplug.generate_code_plug_unplug,                     # UDL - 383, Re for cold unplug

        "( *)Check( +)(\\bsystem\\b|\\bEvent\\b)( +)log( +)for( +)"
        "(\\bShutdown\\b|\\bRestart\\b|\\bCS\\b|\\bs[3,4]\\b|\\bBSOD\\b)( *)":
            code_gen_check_system_log.generate_code_check_system_log,           # UDL - 384, RE for check system logfor <events/Bugcheck>

        "( *)Get( +)(.*)( +)from( +)(\\bOS\\b|\\bBIOS\\b)(( +)using( +)(\\b"
        "task manager\\b|\\bDevice manager\\b|\\bSystem Information\\b|\\b"
        "System Properties\\b))?( *)":
            code_gen_get_system_component_details.
            generate_code_get_system_component_details,                         # UDL - 385, RE for Get <Device_Details> from <Environment>{ using <system_details>}
        
        "( *)Launch( +)(\\bNotepad\\b|\\bHeavyload_Tool\\b|\\bconfig-(.*)\\b)"
        "( *)":
            code_gen_launching_an_application.
            generate_code_launch_the_application,                               # UDL - 386, RE for Launching an application

        "( *)Compare( +)log( +)(.*)( +)with( +)(.*)( *)":
            code_gen_compare_files.generate_code_compare_files,                 # UDL - 394, RE For Compare <log/image> <sourcepath or file> with <destinationpath or file>

        "( *)Run( +)and( +)Verify( +)VTInfo( +)Test( +)is( +)(\\bPass\\b|"
        "\\bFail\\b)( +)in( +)EFI_Shell( *)":
            code_gen_run_vtinfo_tool_for_test_title.
            generate_code_run_vtinfo_tool_for_test_title,                       # UDL - 396, RE for Run  and verify VtInfo Tool

        "( *)Get( +)(.*)( +)of( +)(.*)( +)from( +)device( +)manager( *)":
            code_gen_getting_device_attributes.
            generate_code_get_device_attribute,                                 # UDL - 398, RE for get device attributes from device manager

        "( *)Run( +)TPM.msc( +)and( +)(\\bread\\b|\\bclear\\b|\\binitialize\\b"
        "|\\bown\\b)( +)the( +)TPM( *)":
            code_gen_read_tpm_status.generate_code_read_tpm_status,             # UDL - 404, RE for Run TPM.msc and <read/clear/initialize/own> the TPM

        "( *)Press(.*)(\\bpower\\b|\\breset\\b)( +)button?( *)":
            code_gen_press_buttons_on_board.
            generate_code_press_onboard_button,                                 # UDL - 405, RE for Press <button_name> button { for <number> <seconds/times>}

        "( *)Check( +)(\\bUSB2.0-Pendrive\\b|\\bUSB3.0-Pendrive\\b|"
        "\\bUSB3.1-Pendrive\\b|\\bWinUSB\\b|\\bSUT\\b|\\bUSB3.0-HDD\\b|"
        "\\bUSB2.0-HDD\\b|\\bUSB2.0-SDCard\\b|\\bUSB3.0-SDCard\\b|"
        "\\bUSB4.0-SDCard\\b|\\bType-C-Pendrive\\b|\\bType-C-USB3.1-Pendrive"
        "\\b)"
        "( +)as( +)(\\bHighSpeed\\b|\\bSuperSpeed\\+\\b|\\bSuperSpeed\\b)"
        "( *)($|(( +)in( +)"
        "(\\bHost-System\\b|\\bClient-System\\b)( *)))":
            code_gen_verify_usb_data_transfer_modes.
            generate_code_verify_usb_data_transfer_modes,                       # UDL - 411, RE for check <usb_type> as <variable>

        "( *)READ( +)the( +)value( +)of( +)(\\bEAX\\b|\\bEBX\\b|\\bECX\\b|"
        "\\bEDX\\b)( +)with( +)EAX( *)=( *)([a-zA-Z0-9]+)( +)and( +)ECX( *)="
        "( *)([a-zA-Z0-9]+)( *)":
            code_gen_reading_data_register_values.
            code_gen_reading_data_register_values,                              # UDL - 414, RE for to Read data register values using ASM cpuid

        "( *)Read( +)the( +)value( +)of( +)bit(.*)( +)from( +)(.*)( *)":
            code_gen_read_bit_value.generate_code_read_bit_value,               # UDL - 415, RE for to Read the value of bit<Bit_Number> from Step

        "( *)Set( +)Virtual( +)Battery( +)(\\bAC\\b|\\bDC\\b)( *)":
            code_gen_set_virtual_battery_mode.
            generate_set_virtual_battery_mode,                                  # UDL - 416, Re for Set Virtual Battery <Mode>

        "( *)Calculate( +)((.*)|(step( +)([0-9]+)))( +)(.*)( +)"
        "((.*)|(step( +)([0-9]+)))( *)":
            code_gen_calculate_number.generate_code_calculate_number,           # UDL - 421, RE for Calculate (<Value1>|Step <First_StepNo>) <Operation> (<Value2>|Step <Second_StepNo>){ <Operation2> (<Value3>|Step <Third_StepNo>)}{ <Operation3> (<Value4>|Step <Forth_StepNo>)}

        "( *)Generate( +)Random( +)Number( +)Between( +)(\\bconfig-(.*)\\b|"
        "\\bstep( *)([0-9]+)\\b|\\b([0-9]+))( +)and( +)(\\bconfig-(.*)\\b|"
        "\\bstep( *)([0-9]+)\\b|\\b([0-9]+))( *)":
            code_gen_generate_random_number.
            generate_code_generate_random_number,                               # UDL - 423, RE for Generate Random Number Between <Value1> and <Value 2 >

        "( *)WAIT( +)FOR( +)(\\bconfig-(.*)-(.*)\\b|\\bstep( +)([0-9]+)\\b|"
        "\\b([0-9]+)\\b)( +)SECOND(s*)( *)":
            code_gen_pause_execution.generate_code_pause_execution,             # UDL - 425, RE for WAIT FOR <TIME> SECONDS

        "( *)Read( +)Battery( +)Status( *)($|(( +)from( +)(\\bProducer-System"
        "\\b|\\bConsumer-System\\b|\\bSmartphone\\b\\b)( *)))":
            code_gen_read_battery_status.generate_code_read_battery_status,     # UDL - 429, RE for Read Battery Status {from <system>}

        "( *)Read( +)(\\bS[0,3-5]\\b|\\bDeepS[3-5]\\b|\\bMoS\\b|\\bS0i[1,3]\\b"
        "|\\bCS\\b|\\bSLP-S0\\b|\\bRTD3\\b)"
        "( +)LED( *)=( *)(\\bON\\b|\\bOFF\\b)( *)":
            code_gen_read_the_status_of_led.
            generate_code_read_the_status_of_led,                               # UDL - 430, RE for read led status

        "( *)Set( +)power( +)plan( +)(.*)( +)to( +)(.*)( +)for( +)"
        "(\\bAC\\b|\\bDC\\b)( *)":
            code_gen_set_power_plan.generate_code_set_power_plan,               # UDL - 431, RE for Set power plan <"Variable name"> to <"action"> for <AC/DC>

        "( *)Get( +)boot( +)order( +)list( *)":
            code_gen_get_boot_order.generate_code_get_boot_order,               # UDL - 432, RE for Get boot order list

        "( *)Set( +)boot( +)order( +)(.*)( *)":
            code_gen_set_boot_order.generate_code_set_boot_order,               # UDL - 433 RE for Set boot order <Param1>

        "( *)Set( +)registry( +)(.*)( +)in( +)(.*)( +)=( +)(.*)( *)":
            code_gen_edit_registry.generate_code_edit_registry,                 # UDL - 443, RE For Set registry

        "( *)Connect( +)(\\bDC\\b|\\bAC\\b|\\bVirtual battery\\b|\\bATX\\b|"
        "\\bTypeC-PD-60W\\b|\\bType-C-Charger\\b)( *)":
            code_gen_connect_power_source.generate_code_connect_power_source,   # UDL - 451, RE for Connect <Power Source>

        "( *)Disconnect( +)(\\bATX\\b|\\bDC\\b|\\bAC\\b|\\bCDP-Charger\\b|"
        "\\bWIRELESS-CHARGER\\b|\\bDCP-Charger\\b|\\bTypeC-PD-60W\\b|"
        "\\bUSB-ACA-Charger\\b|\\bUSB-Charger\\b|\\bVirutal battery\\b|"
        "\\bVirtual dock\\b| \\breal battery\\b|\\breal dock\\b|\\bAC brick\\b|"
        "\\busb-powerbank\\b|\\bCDC-Charger\\b|\\bSPD-Charger\\b)( *)":
            code_gen_disconnect_power_source.
            generate_code_disconnect_power_source,                              # UDL - 452, RE for Disconnect <PowerSource>{ if connected}

        "( *)Get( +)entire( +)device( +)list( +)from( +)device( +)manager( *)":
            code_gen_get_device_list_from_devicemanager.
            generate_code_get_devicelist,                                       # UDL - 453, RE for Get entire device list from device manager

        "( *)Verify( +)CPU(( +)core( +)([0-9]+))?( +)ran( +)at( +)"
        "(\\bLFM\\b|\\bHFM\\b|\\bTFM\\b|\\bALL P-STATES\\b)"
        "(( +)from( +)step( +)([0-9]+)( +)log)?( *)":
            code_gen_verification_of_cpu_freq_state.
            generate_code_verification_of_cpu_freq_state,                       # UDL - 455, RE for Verify CPU ran at <parameter>

        "Get( +)c-state( +)for(.*)>(.*)from( +)step( +)([0-9]+)( +)log( *)":
            code_gen_get_package_power.generate_code_get_package_power,         # UDL - 458, RE for Get System State/Get Package Power


        "( *)Get( +)(\\bedp\\b|\\bDP\\b|\\bHDMI\\b)( +)Display( +)(\\bBrightness\\b)":
            code_gen_check_brightness_of_display_device.
                generate_code_check_brightness_of_display_device,               # UDL - 459, RE for Get display properties

        "( *)Clear( +)all( +)(\\bevent_viewer\\b)( +)logs( *)":
            code_gen_clear_event_viewer_logs.
            generate_code_clear_event_viewer_logs,                              # UDL - 463, RE for Clear all event viewer logs

        "( *)Verify( +)Event( +)viewer( +)for( +)(.*)( *)":
            code_gen_verify_event_viewer.
            generate_code_verify_event_viewer,                                  # UDL - 464, RE verify event viewer for <value>

        "( *)Verify( +)(\\bUSB2.0-Pendrive\\b|\\bUSB3.0-Pendrive\\b|"
        "\\bUSB-Keyboard\\b|\\bUSB-Mouse\\b|\\bUSB-Pendrive\\b|"
        "\\bUSB3.0-HDD\\b|\\bType-C-USB3.0-Pendrive\\b|\\bPS2-keyboard\\b|"
        "\\bUSB2.0-HDD\\b|\\bUSB-LAN\\b|\\bUSB3.1-SSD\\b|"
        "\\bType-C-USB3.1-Gen2-SSD\\b|\\bALS-Sensor\\b|"
        "\\bLinear-Acceleration-Gravity-Sensor\\b|\\bInclinometer-Sensor\\b|"
        "\\Device-Orientation-Sensor\\b|\\bLinear-Acceleration-Sensor\\b|"
        "\\bAccelerometer-Sensor\\b|\\bMagnetometer-Sensor\\b|"
        "\\bAltimeter-Sensor|\\bProximity-Sensor\\b|\\bUSB3.1-Gen2-SSD\\b)"
        "( +)functionality"
        "(( *)$|( +)in( +)"
        "(\\bOS\\b|\\bEFI\\b|\\bBIOS\\b)( *)$)":
            code_gen_verify_device_functionality.
            generate_code_check_device_functionality,                           # UDL - 465, RE For Verify <Param1> functionality in Param2>

        "( *)Perform( +)Start( +)Capture( +)of( +)(\\bonline_BIOS\\b|"
        "\\boffline_BIOS\\b|\\bBIOS\\b)( +)log( *)":
            code_gen_capture_bios_log.generate_code_capture_bios_log,           # UDL - 468, RE for Perform Start/Stop Capture BIOS log

        "( *)Perform(.*)Capture( +)of( +)(\\bdebug\\b)( +)log( *)":
            code_gen_capture_debug_log.generate_code_capture_debug_log,         # UDL - 468, RE for Perform Start/Stop Capture Debug log

        "( *)Verify( +)(\\bIntel(.*)\\b|\\bUSB(.*)\\b|\\bSATA(.*)\\b|"
        "\\bPCIe(.*)\\b|\\bsensors\\b|\\buSD-Class10-UHS\\b|\\bSuperDuperVSC"
        "\\b|\\b3.5mm-Jack-Headset\\b|\\bLauterbach PODBUS USB Controller "
        "(USB3)\\b|\\bTPM2VSC\\b|\\bINVDIMM Device\\b|\\bBT(.*)\\b|\\bType-C"
        "(.*)\\b|\\bSDXC\\b|\\bM.2(.*)\\b|\\bGNSS(.*)\\b|\\bSDHC\\b|\\bWindows"
        "(.*)\\b|\\bNexus-Tablet\\b|\\bThunderbolt(.*)\\b|\\bZPODD\\b|\\bMicro"
        "(.*)\\b|\\bHigh(.*)\\b|\\bSD(.*)\\b|\\bISS(.*)\\b|\\bUCMCx connector "
        "manager\\b|\\bHID(.*)\\b|\\bwireless bluetooth\\b|\\bDP(.*)\\b|"
        "\\bSynaptics Precision Touch Pad\\b|\\bAVstream Camera device\\b|"
        "\\bHDMI(.*)\\b|\\bStandard(.*)\\b|\\bAMD(.*)\\b|\\beDP_Display\\b|"
        "\\b16550A-compatible COM port\\b|\\beMMC storage drive\\b|\\bTBT(.*)"
        "\\b|\\bRealtek High Definition Audio\\b|\\bPersistent Memory Disk\\b|"
        "\\bbarometer\\b|\\bNXP Near Field proximity\\b|\\bVGA_Display_Audio"
        "\\b|\\bNvidia Gforce 840M\\b|\\bMicrosoft Basic Display adapter\\b|"
        "\\bDell_Display_Audio\\b|\\bambient light sensor\\b|\\baccelerometer"
        "\\b|\\bCSME\\b|\\bDPTF\\b|\\bGFx\\b|\\bUCSI USB connector manager\\b|"
        "\\btrusted platform module 2.0\\b|\\bIR_Sensor\\b|\\bConfig-Header-"
        "Value\\b|\\bakito-quad-tbt3-storage\\b|\\blacie-tbt2-storage\\b|"
        "\\bWWAN\\b|\\bSandisk-USB3.1-gen2-HDD-Extreme-900\\b|\\bCamera(.*)"
        "\\b|\\bSkycam\\b|\\bSystem Devices\\b|\\bTablet\\b|\\bSmartPhone\\b|"
        "\\bOV13858 _Camera_Sensor\\b|\\bFinger-Print-Sensor\\b|"
        "\\bMicro-sdcard\\b|\\bconfig-(.*)\\b|\\bPedometer Sensor\\b)"
        "(( +)is( +)hidden)?(( +)under( +)(.*))?( +)in( +)"
        "(\\bDevice Manager\\b|\\bAction Manager\\b|\\bSensor Viewer\\b)"
        "(( +)in( +)(\\bhost\\b|\\bType-C-SUT1\\b|\\bType-C-SUT2\\b|"
        "\\bType-C-SUT3\\b))?( *)":
            code_gen_verify_device_enumeration.
            generate_code_verify_device_enumeration,                            # UDL - 469, RE for Verify <Device name> {under <parent category>} in device manager

        "( *)Verify(( +)online)?(( +)(\\b480p\\b|\\b720p\\b|\\b1080p\\b|\\b4K"
        "\\b|\\bHD\\b))?( +)(\\baudio\\b|\\bvideo\\b|\\bAV\\b)( +)playback( +)"
        "(( +)Quality)?on( +)(\\beDP-Display\\b)( *)":
            code_gen_audio_video_playback_verification_on_device.
            generate_code_verify_playback_on_device,                            # UDL - 472, RE for verify playback verification

        "( *)Verify( +)System( +)is( +)in( +)(\\bAC\\b|\\bDC\\b|\\bAC\+DC\\b|"
        "\\bG3\\b)( +)Power( +)Mode( *)":
            code_gen_verify_power_mode.generate_code_verify_power_mode,         # UDL - 477, RE for Verify System is in <Parameter> Power Mode

        "( *)Perform( +)(\\bEnable\\b|\\bDisable\\b)( +)of( +)(\\bWiFi\\b|"
        "\\bHibernate\\b)( +)in( +)OS( *)":
            code_gen_enable_disable_module.
            generate_code_enable_disable_module,                                # UDL - 478, RE for <Enable/Disable> <Module> in OS

        "( *)Apply( +)workload( +)for( +)([0-9]+)( +)seconds( +)with( +)"
        "([0-9]+)%( *)":
            code_gen_apply_workload.generate_code_apply_workload,               # UDL - 480, RE for Apply Workload

        "( *)Start( +)(\\bC-State_P-State\\b|\\bC-state_SLP-S0\\b|\\bP-State"
        "\\b|\\bCM-states\\b|\\bPCIe-LPM\\b|\\bSys-State\\b|\\bT-state\\b|"
        "\\bSATA-LPM\\b|\\bCpu package power\\b|\\bPSR-State\\b|\\bS-state\\b|"
        "\\bGT-State\\b|\\bConfig-Header-Value\\b|\\bRTD3\\b|\\bS0ix states"
        "\\b|\\bSLP-S0\\b|\\bIR-State\\b|\\bC-state\\b|\\bD-state\\b|"
        "\\bs-state\\b)( +)capture( *)":
            code_gen_start_stop_capture.code_gen_start_stop_capture,            # UDL - 495, RE for Start State Capture

        "( *)Stop( +)(\\bC-State_P-State\\b|\\bC-state_SLP-S0\\b|\\bP-State"
        "\\b|\\bCM-states\\b|\\bPCIe-LPM\\b|\\bSys-State\\b|\\bT-state\\b|"
        "\\bSATA-LPM\\b|\\bCpu package power\\b|\\bPSR-State\\b|\\bS-state\\b|"
        "\\bGT-State\\b|\\bConfig-Header-Value\\b|\\bRTD3\\b|\\bS0ix states"
        "\\b|\\bSLP-S0\\b|\\bIR-State\\b|\\bC-state\\b|\\bD-state\\b)( +)"
        "capture( *)":
            code_gen_start_stop_capture.code_gen_start_stop_capture,            # UDL - 496, RE for Stop state capture

        "( *)Read( +)the( +)post( +)code(( *)=( *)(\\b(Config-(.*)-(.*))\\b|"
        "\\b([a-zA-z0-9]+)\\b))?( *)":
            code_gen_read_post_code.generate_code_read_post_code,               # UDL - 508, RE for Read the Post code { = <postcode> }

        "( *)Do( +)(\\bdecrease\\b|\\bIncrease\\b)( +)display( +)brightness( +)of( +)"
        "(\\beDP-Display\\b)(.*)( *)":
            code_gen_modify_display_brightness.
                generate_code_modify_display_brightness,                        # UDL - 514, RE for Modification of display brightness


        "( *)Verify( +)display( +)quality( +)for( +)(\\beDP-Display\\b)( *)":
            code_gen_verify_display_with_display_property.
            generate_code_verify_display_with_display_property,                 # UDL - 520, RE for verify display with display properties

        "( *)Parse( +)PCI( +)dump( +)from( +)step( +)([0-9]+)( +)log( +)for( +)"
        "offset( +)(([a-fA-F0-9]+))":
            code_gen_parse_offset_value.generate_code_parse_offset_value,       # UDL - 529, RE for Parse PCI dump from Step <StepNo> log for offset <Offset_Value>

        "( *)Perform( +)(\\bP-State\\b|\\bC-State\\b)( +)cycling( +)for( +)"
        "([0-9]+)( +)seconds( +)with( +)([0-9]+)( +)percent( +)workload( *)":
            code_gen_perform_pc_state_cycling.
            generate_code_perform_pc_state_cycling,                             # UDL - 540, RE for Perform <X-State> cycling for <Duration > seconds with< Load%> Workload

        "( *)Repeat( +)step(s*)( +)([0-9]+)(( +)to( +)([0-9]+))?(( +)for( +)"
        "(\\bconfig-(.*)-(.*)\\b|\\bstep( +)([0-9]+)\\b|\\b([0-9]+))( +)time"
        "(s*))?( *)":
            code_gen_repeat_steps.generate_code_repeat_steps,                   # UDL - 546, RE for Repeat steps <m> [to <n>] [for <x> times]: with steps as parameter

        "( *)Copy( +)file( +)from( +)(\\bSUT\\b|\\bUSB3.0-HDD\\b|"
        "\\bUSB3.0-Pendrive\\b|\\bUSB2.0-Pendrive\\b|\\bUSB3.1-SSD\\b|"
        "\\bType-C-USB3.1-Pendrive\\b|\\bUSB3.1-Pendrive\\b)( +)to( +)"
        "(\\bSUT\\b|\\bUSB3.0-Pendrive\\b|\\bUSB3.0-HDD\\b|\\bUSB3.0-Pendrive"
        "\\b|\\bUSB2.0-Pendrive\\b|\\bUSB3.1-SSD\\b|"
        "\\bType-C-USB3.1-Pendrive\\b|\\bUSB3.1-Pendrive\\b)( *)":
            code_gen_copying_file_from_src_to_dest.
            generate_code_copying_file_from_source_to_destination,              # UDL - 547, RE for Copy file from <source> to <destination>

        "( *)verify( +)if( +)system( +)is( +)in( +)"
        "(\\bOS\\b|\\bBIOS Setup\\b|\\bEDK Shell\\b)( *)":
            code_gen_verifying_system_in_os.
            generate_code_verifying_system_in_os,                               # UDL - 550, RE for verifying system is in os

        "Read( +)residency( +)of( +)(\\bsystem\\b)( +)in( +)(\\bS3\\b)( *)":
            code_gen_read_residency.generate_code_read_residency,               # UDL - 552, RE for to read residency of device

        "( *)toggle( +)(\\bvirtual battery\\b|\\bwifi\\b|\\blid\\b|"
        "\\bVirtual-Dock\\b|\\bVirtual-unDock\\b|\\bunDock\\b|\\bDock\\b|\\b"
        "onboard\\b)(( +)(.*))?( +)switch( *)":
            code_gen_onboard_switch_toggle.generate_code_toggle_switch,         # UDL - 558, RE for Toggle <virtual battery/wifi/lid> switch

        "( *)Wake( +)(\\bSystem\\b)( +)from( +)(\\bS[3-5]\\b|\\bS0i[1,3]\\b|"
        "\\bCMS\\b|\\bDeepS[3-5]\\b)"
        "( +)using( +)(\\bPWR_BTN\\b|\\bUSB-LAN\\b|\\bUSB-Keyboard\\b"
        "|\\bLID_Action\\b|\\bLAN\\b|\\bUSB-MOUSE\\b|\\bKeyboard\\b)( *)":
            code_gen_wake_up_from_sx.generate_code_wake_up_from_sx,             # UDL - 562, RE for wake sut from sx

        "( *)Select( +)(.*)( +)from( +)(.*)( +)in( +)(\\bBIOS\\b|\\bMEBx\\b)"
        "( +)and( +)choose( +)(\\bEnter\\b|\\bEsc\\b|\\bUnpair\\b|"
        "\\bDisconnect\\b)( *)":
            code_gen_option_selection_in_bios.
            generate_code_option_selection_in_bios,                             # UDL - 569, RE for Option Selection in BIOS

        "( *)Read( +)(.*)( +)state":
            code_gen_read_me_state.generate_code_read_me_state,                 # UDL - 575, RE for Read ME State

        "( *)Navigate( +)to( +)the( +)following( +)menu:( *)":
            code_gen_gui_tool_navigation.generate_code_gui_tool_navigation,     # UDL - 577, RE for to navigate to destination and do required action

        "( *)verify( +)PAVP( +)test( +)in( +)(\\bHeavy\\b|\\bLite\\b)"
        "( +)mode( *)":
            code_gen_pavp_test_modes.generate_code_pavp_test_modes,             # UDL - 581, Re for PAVP test mode

        "( *)Read( +)(\\bBios Guard\\b|\\bucode\\b|\\bTXE FW\\b|\\bCSE FW\\b"
        "|\\bMRC\\b)( +)version( +)under( +)FVI( +)from( +)OS( *)":
            code_gen_read_file_version_from_os.
            generate_code_read_file_version_from_os,                            # UDL - 582, RE for Read SMBIOS Structures for <Variable>

        "( *)convert( +)(\\bstep( +)([0-9]+)\\b|\\bconfig-(.*)\\b)( +)(\\bhex"
        "\\b|\\bdecimal\\b|\\bocta\\b|\\bbinary\\b)( +)to( +)(\\bhex\\b|"
        "\\bdecimal\\b|\\bocta\\b|\\bbinary\\b)":
            code_gen_conversion_of_numerical_format.
            generate_code_conversion_of_numerical_format,                       # UDL - 585, RE For Convert <param 1> <param 2> to <param 3>

        "( *)Verify( +)if( +)(.*)( +)occurs( +)(\\bafter\\b|\\bbefore\\b)( +)"
        "(.*)( +)from( +)step( +)([0-9]+)( +)log":
            code_gen_verify_place_of_occurrence.
            generate_code_verify_place_of_occurrence,                           # UDL - 587, RE for to Verify the place of occurance

        "( *)Hot-plug( +)(\\bUSB2.0-Pendrive\\b|\\bUSB3.0-Pendrive\\b|"
        "\\bUSB3.0-hub\\b|\\bUSB-Keyboard\\b|\\bUSB-Mouse\\b|\\bUSB2.0-HUB\\b|"
        "\\bType-C-to-A-dongle\\b|\\bUSB3.0-HDD\\b|\\bUSB-Pendrive\\b|\\bUSB3.1"
        "-SSD\\b|\\bType-C-USB3.1-Pendrive\\b|\\bType-C-USB3.1-Gen2-SSD\\b|"
        "\\bUSB-HUB\\b|\\bType-C-USB3.0-Pendrive\\b|\\btype-c-dock\\b|"
        "\\bHDMI-Display\\b|\\bDP-Display\\b|\\bUSB2.0-HDD\\b|"
        "\\bType-C-PD-Charger\\b)"
        "((( +)to( +)(\\bUSB2.0-Type-A\\b|\\bUSB3.0-hub\\b|\\bUSB3.0-Type-A\\b|"
        "\\bType-C-\\b|\\bHDMI\\b|\\bDP\\b)( +)port)?)?( *)":
            code_gen_plug_unplug.generate_code_plug_unplug,                     # UDL - 593, RE for Hot-plug

        "( *)Hot-Unplug( +)(\\bUSB2.0-Pendrive\\b|\\bUSB3.0-Pendrive\\b|"
        "\\bUSB3.0-hub\\b|\\bUSB2.0-HUB\\b|\\bUSB-Keyboard\\b|\\bUSB-Mouse\\b|"
        "\\bType-C-USB3.1-Pendrive\\b|\\bType-C-to-A-dongle\\b|\\bUSB3.1-SSD\\b"
        "|\\bUSB-Pendrive\\b|\\bUSB3.0-HDD\\b|\\bType-C-USB3.1-Gen2-SSD\\b|"
        "\\bType-C-USB3.0-Pendrive\\b|\\bUSB2.0-HDD\\b|\\bDP-Display\\b|\\bHDMI-Display\\b)"
        "((( +)from( +)(\\bUSB2.0-Type-A\\b|\\bUSB3.0-Type-A\\b|\\bUSB-HUB\\b"
        "|\\bUSB3.0-Type-A-Vertical\\b|\\bUSB3.0-Type-A-\\b|\\bType-C-\\b)"
        "( +)port)?)?( *)":
            code_gen_plug_unplug.generate_code_plug_unplug,                     # UDL - 594, RE for Hot-Unplug

        "( *)Get( +)battery( +)charge( +)to( +)([0-9]+)( +)percent( *)":
            code_gen_battery_charge_discharge_operation.
                generate_code_battery_charge_discharge_operation,               # UDL - 603, RE for Get battery charge{ of <System_Type>} to (<Charge_Percent> percent|Value from Step <StepNo>){ if current charge <Operator> <Current_Percent> percent}

        "( *)Write( +)PCI( +)Register( +)of( +)Bus( +)(.*)( +)"
        "Device( +)(.*)( +)Function( +)(.*)( +)offset( +)(.*)( +)(.*)":
            code_gen_write_pci_bdf.generate_code_write_pci_bdf,                 # UDL - 606, RE for write PCI register

        "( *)Flash( +)(\\bConfig-(.*)\\b|\\bRelease\\b|\\bDebug\\b|"
        "\\bPerformance\\b|\\bCorporate\\b|\\bconsumer\\b|\\bprod\\b|"
        "\\bpreprod\\b|\\blpc\\b|\\bespi\\b|\\bNR-performance\\b|\\bTest\\b|"
        "\\bRelease-FSP\\b|\\bDebug-FSP\\b|\\bPerformance-FSP\\b|\\bFSP\\b|"
        "\\bfsp-vs-edkwrapper\\b|\\bfsp-gcc-edkwrapper\\b|\\bIntel Test "
        "Menu\\b|\\bTest-menu-enabled\\b)"
        "( +)(\\bBIOS\\b|\\bIFWI\\b|\\bKSC\\b|\\bBGUP\\b|\\bKSC BGUP\\b|"
        "\\bNVM\\b)?(( *)$|( +)(on( +)(\\bSPI\\b|\\bEMMC\\b|\\bUFS\\b)( *)))?"
        "(( *)$|( +)((\\busing\\b|\\bby\\b)( +)(\\bDNX\\b|\\bCAPSULE\\b|"
        "\\bFFT\\b|\\bTTK\\b|\\bFPT\\b|\\bMSFT FFU\\b|\\bTenLira\\b)( *)))?"
        "(( *)$|( +)(from( +)(\\bOS\\b|\\bEFI\\b|\\bWOS\\b|\\bAOS\\b)( *)))":
            code_gen_flash_bios.generate_code_flash_bios,                       # UDL - 607, RE for Flash <type> <BIOS/IFWI/KSC/BGUP> {using <method>}

        "( *)Verify( +)if( +)battery( +)is( +)(\\bCharging\\b|\\bDischarging"
        "\\b)(( +)in( +)(\\bS[3-5]\\b|\\bDeepS[3-5]\\b|\\bCS\\b|\\bdMoS\\b|"
        "\\bcMoS\\b|\\bS0i[1,3]\\b|\\bSLP_S0\\b|\\bCmoff\\b|\\bCM3\\b|"
        "\\bME-PG\\b|\\bCM3-PG\\b|\\bCmoff-PG\\b)( +)State)?( *)":
            code_gen_verifying_battery_charging_and_discharging.
            generate_code_verifying_battery_charging_and_discharging,           # UDL - 613, RE for Verify if battery is <Charging/Discharging> {in <SX> State}

        "( *)Check( +)USB( +)(\\bHS\\b|\\bSS\\b|\\bType-A\\b|\\bType-C\\b)"
        "( +)Port( +)(.*)( +)for( +)(.*)( *)":
            code_gen_check_usb_port_details_and_capabilities.
            generate_code_check_usb_port_details_and_capabilities,              # UDL - 656, RE for usb port details and its capability

        "( *)Run( +)BKM( +)(.*)( *)":
            code_gen_run_bkm_test_case.code_generate_run_bkm_test_case,         # UDL - 1739, RE for Run BKM Test case

        "( *)Click( +)on( +)(.*)"
        "( +)and( +)read( +)status( +)as( +)(.*)( +)in( +)"
        "(\\bSensorviewer tool\\b)":
            code_gen_read_sensor_status.
            generate_code_read_sensor_status,                                   # UDL - 1750, RE for Read sensor status from sensor viewer tool

        "( *)Read( +)(\\bThermal\\b)( +)sensor(.*)( +)using( +)(\\bDPTF\\b)"
        "( +)tool(.*)( *)":
            code_gen_read_and_compare_sensor_data.
            generate_code_read_and_compare_sensor_data,                         # UDL - 1755, RE for Read and compare sensor data

        "( *)Get( +)value( +)for( +)(.*)( +)from( +)step( +)[0-9]{1,2}( +)"
        "log( *)":
            code_gen_get_value_from_log.generate_code_get_value_from_log        # UDL - 1829, RE for Get value for '<Search_String>'{ under <Log_Section>} from step <StepNo> log{ in <System_Type>}

    }
