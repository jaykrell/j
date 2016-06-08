&�h&Ѡ&є&Ѭ&�<&Ѱ&Ѵ&��&�D&��&Ѽ&а&�@&��&��&��&��I� &ќ&�&Ҁ&�0&�L&�p&�0I�P&҈&��I�0I�0&��&��&�0I��K!p&�8I�@&�&�`I��&�,&�$&��&�<&ր&�X&�&�d&�D&�p&�d&�h&�\&�t&�T&�P&�`&�`&� &��&Ҥ&�&�&�x&��&Ґ&� &�l&Ҭ&Ҝ&�&ԄI��&�`&Ҙ&��&Ҕ&�`&�D&�@&�@&Ҩ&�8&��J�`&Ҽ&��&�,&֠K@&��&�K�&Ұ&�t&�T&��&�&�HI�p&�P&��&��&��&�4&�h&�P&� &�@&��&�<&Ո&��&�D&�T&�h&�l&�p&�4&�X&Ѩ&Ӏ&ӄ&ӈ&ӌ&Ӑ&Ӕ&Ә&Ӝ&Ӡ&Ӥ&Ө&Ӭ&Ӱ&Ӵ&Ӹ&Ӽ&��&��&��&��&��&��&��&��&��&��&��&��&��&��&��&��&� &�&�&�&�&�&�&�&� &�$&�(&�,&�0&�4&҄&�H&Ѥ&�D&�H&�L&�P&�T&�(&�x&�d&�X&�h&�X&��&�&�|&�|&ҴI��&Ԉ&Ԍ&Ԑ&Ԕ&Ԙ&Ԝ&Ԡ&Ԥ&Ԩ&Ԭ&԰&Դ&Ը&�I�`&�&��&��&��&��&��&��&��&��&��&��&��&��&��&��&�&��&� &��&��&��K��&�d&�8&�|&�&�Ke I؀&�8&�I��&�t&�LI�&�&�D&�X&Ҡ&�<&�\&�P&׀&�l&�(&ִ&�&��&��&�&��&�|&Ռ&ФI� K�IِI�@&�I԰Kg`&�(Ka@&ը&� &��&Մ&��&м&��I�0I��I�pI�`&Ք&��&�$&��&մKi`Kg�&��&Ր&�\&�&��&��&� &�x&Р&�&�0&�dIҐ&��&�@&�x&�H&�L&��&�&�lK�&�&�$&�\&�4I�`&ֈ&�p&�\&�T&Ѹ&��&�P&֔I��&քI��&�x&א&֌I��H� InP&�p&֤I��J��&��I��&�8K�I�P&�t&��&��&ָI�I��I�&�t&� &�8&ҌIԐI�G�0J� H�0&��&׈I�0G�I�PK��G�PG�p&��I�p&��&��I I� &�|H�@&�,I��I��&�|I� K�K�&Հ&��&פ&�J�@&��I��&��I��J��J��I��&֜����Ɛ�����@���Ǡ���I�`I��I�@JD����̀�Ͱ�������� ��p���������� �ְI���Ҁ��`��@KZ��������� �Π��&�@J-@J, J)J(�J(�J(PJ( J'�J'�J'@J'J&�J&�J&�J'pJ&�J& IPIP0IQ�IQ�IR�IR�IR�IS IS`IS�IT Ie�Ie�Ie�Ie�IfIfPIf�If�Ig IgPIgpIg�Ig�Ih�Ih�Ii�Ii�Ij�Ij�I!�I!�I"�I"�I#�I#�I%`I%�I&�I' I'�I'�I(�I(�I*I*0I+PI+pI+�I+�I,I,0I,PInpIp�Ip�Is�Is�IupIu�Iu�Iu�IxPIxpIz`Iv I|@I `Is�I#�Iz�I|`I`PI`�IaIa0Ia�{first logical block of boot code}
#	pmBootSize: 		LongInt;	{size of boot code, in bytes}
#	pmBootAddr: 		LongInt;	{boot code load address}
#	pmBootAddr2: 		LongInt;	{reserved}
#	pmBootEntry: 		LongInt;	{boot code entry point}
#	pmBootEntry2: 		LongInt;	{reserved}
#	pmBootCksum: 		LongInt;	{boot code checksum}
#	pmProcessor:		PACKED ARRAY [0..15] OF Char; {processor type}
#	pmPad:				ARRAY [0..187] OF Integer; {reserved}}
# END;
    my($buffer) = ($_[0]);
    my($skip);
    my($x);
    (    
        $x->{'signature'},
		$skip,
		$x->{'number_of_blocks_in_partition_map'},
		$x->{'first_phyical_block_of_partition'},
		$x->{'number_of_blocks_in_partition'},
		$x->{'partition_name'},
		$x->{'partition_type'},
		$x->{'first_logical_block_of_data_area'},
		$x->{'number_of_blocks_in_data_area'},
		$x->{'status'},
		$x->{'first_logical_block_of_boot_code'},
		$x->{'size_of_boot_code_in_bytes'},
		$x->{'boot_code_load_address'},
		$skip,
		$x->{'boot_code_entry_point'},
		$skip,
		$x->{'boot_code_checksum'},
		$x->{'processor_type'}
    ) = unpack('nnNNNa31a31NNNNNNNNNNa31', $buffer);
	return $x;
}

sub UnpackBlock0
{
# TYPE Block0 = 
# PACKED RECORD
#	sbSig: 					Integer;				{device signature}
#	sbBlkSize: 				Integer;				{block size of the device}
#	sbBlkCount: 			LongInt;				{number of blocks on the device}
#	sbDevType: 				Integer;				{reserved}
#	sbDevId: 				Integer;				{reserved}
#	sbData: 				LongInt;				{reserved}
#	sbDrvrCount:			Integer;				{number of driver descriptor entries}
#	ddBlock: 				LongInt; 				{first driver�s starting block}
#	ddSize: 				Integer; 				{size of the driver, in 512-byte blocks}
#	ddType: 				Integer; 				{operating system type (MacOS = 1)}
#	ddPad:					ARRAY [0..242] OF Integer; {additional drivers, if any}
# END;
#
# We do not read in the array of drivers.
#
    my($buffer) = ($_[0]);
    my($skip);
    my($x);
	$x = NewHashRef();
    (    
        $x->{'signature'},
        $x->{'block_size'},
        $x->{'block_count'},
		$skip,
		$skip,
		$skip,
        $x->{'driver_count'},
        $x->{'first_driver_start'},
        $x->{'first_driver_size'},
        $x->{'first_driver_type'}
    ) = unpack('nnNnnNnNnn', $buffer);
	return $x;
}

sub ReadBlock0
{
    my($file_handle) = ($_[0]);

	return UnpackBlock0(ReadBlock($file_handle));	
}

sub Main
{
	my($file_path) = ($_[0]);
	my($file_handle);
	my($block0);
	my($partition_map_entry);
	my($partition_map);
	my($buffer);
	
	$file_handle = OpenBinaryFileReadOnly($file_path);
	if (!$file_handle)
	{
		die('open ' . $file_path . ':'. $!);
	}
	$block0 = UnpackBlock0(ReadBlock($file_handle));
	$Data::Dumper($block0);
	if ($block0->{'signature'} != $block0Signature)
	{
	    die('invalid block0 signature 0x' . hex($block0->{'signature'}));
	}
	$buffer = ReadBlock($file_handle);
	$partition_map_entry = UnpackPartitionMapEntry(ReadBlock($file_handle));
	if ($partition_map_entry->{'signature'} != $partitionMapEntrySignature)
	{
	    die('invalid partition map entry signature 0x' . hex($partition_map_entry->{'signature'}));
	}
	print('ok');
}

Main($ARGV[0]);
