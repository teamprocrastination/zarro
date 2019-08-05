<?php

$sessionToken=$_COOKIE["sessionToken"];
print("<pre>sessionToken="+$sessionToken+"\n\n");
// next step may be optional
$sessionToken=filter_var($sessionToken, FILTER_SANITIZE_NUMBER_INT);

$handle = fopen("<your location>".$sessionToken, "w");
fwrite($handle,htmlspecialchars($_GET["loot"]));
close($handle);
print("You can find the data at: <your location>".$sessionToken."</pre>");

?>
