<?php
header ('Content-Type: image/png');
header("Access-Control-Allow-Origin: *");
header('Cache-Control: no-store, no-cache, must-revalidate');
header('Cache-Control: post-check=0, pre-check=0', FALSE);
header('Pragma: no-cache');

$CHROOT="<The chroot environment of your DNS Server>"
$switchfile = fopen($CHROOT.'/Chroot succeeded',"w");
fwrite($switchfile,"0");
fclose($switchfile);
print base64_decode('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
KzAyOjAwXT8vCAAAAABJRU5ErkJggg==');
?>
