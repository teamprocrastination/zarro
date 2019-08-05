<?php
header("Access-Control-Allow-Origin: *");
header('Cache-Control: no-store, no-cache, must-revalidate');
header('Cache-Control: post-check=0, pre-check=0', FALSE);
header('Pragma: no-cache');
?>
<html>
<head>
<title>Let's do it</title>
</head>
<!-- This will read the cookie from the iframe context and reuse it for a POST -->
<body>
<form action="/xml/getter.xml" method="post">
<label>Token</label><input type="text" name="token" value="<?php
print $_COOKIE["sessionToken"];
?>">
<label>fun</label><input type="text" name="fun" value="123">
<input type="submit">
</form>
</body>
</html>
