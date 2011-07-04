<?php
   $locale = $_POST['locale'];
   $data = $_POST['data'];   
   
   $file = fopen($locale.'.json', 'w+');
   fwrite($file, $data);
   fclose($file);
?>
