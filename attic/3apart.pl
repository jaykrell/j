&�|&�(&�&� &��&�&�x&�`&�0&Р&�,I��&�4&�\&�<&Ѹ&�D&�H&�d&�P&ָ&�d&�0&�&��I��&�|&�,&�X&�T&�x&��&֌&֔I�&քI��&�x&��&�PI�PH� In�&�p&�8I�@J�@&�XI�@&հKPI��&��&Մ&�t&ֈI�`I� I�`&��&�|&�8&ҌI��I�G�0J�pH�0&��&�$IאG�I��K� G�PG�p&אI��&��&�4IPI�p&֜H�@&��I�@I�&�DI��&��K `&��&֠&פ&�J��In�Iݠ&��I� J�0J��I�&�P����Ɛ�����@���Ǡ���I��I�@I��JH�����̀�Ͱ�������� ��p���������� �ְI�P�Ҁ��`��@K`P�������� �Π��&�pJ1�J0pJ-�J-`J- J,�J,�J,`J,0J+�J+�J+`J+@J*�J+�J+J*pIP@IP`IQ�IQ�IR�IR�IS IS0IS�IS�IT0Ie�Ie�If If If@If�If�Ig Ig0Ig�Ig�Ig�Ig�Ih�Ih�Ii�Ij Ik Ik I!�I!�I"�I"�I#�I$I%�I%�I'I'0I( I( I) I) I*@I*`I+�I+�I+�I+�I,@I,`I,�In�Iq Iq It It Iu�Iu�IvIv0Ix�Ix�Iz�IvPI|�I �Is�I#�Iz�I|�I`�I`�Ia@Ia`Ib Ib@Ib`Ib�I�PIb�Ic IcPId`Id�Ie�I�I� I�`I��I��I�@I� I��I��I��I��I��I� I�pI��I��I�PI��I�0I��I�I��I��I��I��I��I��I�@I��I�@KS�K<PK&pK#�K#�K$�K$�IF I��K#�K"@I��K:�K$�K#@IE@IBpIb���p�ѐ��@K�K�KPKpK�K�K�KK0KPK�K K0KPKpK�K0K�K�K��������@I� �����p�����@������Kf Kf�I�`I���PK<�I� JS@I J�J�JWPJ�J�JJ 0J%PI\pIWPK�J�I��J�`���J�0I� K��IڠJHJH@I�`I�`K�K`J�K0I�`I�KfPI��I�`I�pJ�PKA�K:�I��K I��I� I��JH�I Kf�I��I��I��K@J�JR�I��I� I�0G��I�`J�PJ��J��J�0J��J��J��J��J�0J�J�0J�`J� J�PJ�pJ��J��J�J�@J�pJ��J��J��J�0J�`J��J��J��J� I�0I��I��K�J��K�KJ�PJ��J��J��J�PJ��J��K  K  K @K �K �K K@KpK�K�K K�K�K�K�K K KPKpK�K@KpK�K�KKPK�K�K�K@K�K�K K@KpK�K K0K�K�K�K	@K	�K	�JI K	�K
 K
`K
�K
�KK@K�K�K�KPKpK�J�K�J��Ka�I�KIA0IA I@�I@�I@pI@0I?�I?�I?�I?PI?0I>�I>�I>pI>PI>0I>I=�I=�I=�I= I<�{first logical block of boot code}
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
