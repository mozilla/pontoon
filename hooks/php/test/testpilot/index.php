<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<?php require_once('../../pontoon.php'); ?>
	<?php Pontoon::header('http://localhost/pontoon/hooks/php/test/testpilot/pontoon.json'); ?>
	<meta http-equiv="content-type" content="text/html; charset=utf-8" />
	<title><?php echo _w('Mozilla Labs Test Pilot')?></title>
	<link rel="stylesheet" type="text/css" media="all" href="screen.css" />
    <script type="text/javascript">
      var s_account="mozillatestpilotmozillalabscom";
    </script>
</head>
<body>

		<div id="container">
		
			<div id="logo"><a href="http://labs.mozilla.com"><img src="images/logo.png" border="0"></a></div>
			
			<div id="download"><div id="downloadsource" class="button" onclick="window.location='https://addons.mozilla.org/services/install.php?addon_id=testpilot'"><img class="downloadButton" src="images/download_arrow.png"> <span class="downloadH1"><?php echo _w('Become a Test Pilot!')?></span> </div></div>
			<div id="content">
			
				<div class="button">
			
					<span class="<?php echo ($_GET['page'] == 'home.php') ? "menuOn" : "menuItem"; ?>"><a href="?page=home.php"><?php echo _w('Home')?></a></span>
					<span class="<?php echo ($_GET['page'] == 'testcases.php') ? "menuOn" : "menuItem"; ?>"><a href="?page=testcases.php"><?php echo _w('Test Cases')?></a></span>
					<span class="<?php echo ($_GET['page'] == 'principles.php') ? "menuOn" : "menuItem"; ?>"><a href="?page=principles.php"><?php echo _w('Guiding Principles')?></a></span>
					<span class="<?php echo ($_GET['page'] == 'privacy.php') ? "menuOn" : "menuItem"; ?>"><a href="?page=privacy.php"><?php echo _w('Privacy Policy')?></a></span>
				
				</div>
				
				<?php
					if (isset($_GET['page'])) {
					    include $_GET['page'];
					} else {
						include 'home.php';
					}					
				?>
				
				<div id="links">
				
					<div class="home_callout"><img class="homeIcon" src="images/home_computer.png"> <a href="http://labs.mozilla.com/projects/test-pilot/"><?php echo _w('Test Pilot Blog &raquo;')?></a></div> <br>
					
					<div class="home_callout"><img class="homeIcon" src="images/home_upcoming.png"><a href="https://wiki.mozilla.org/Labs/Test_Pilot"><?php echo _w('Test Pilot Wiki &raquo;')?></a></div> <br>
					
					<div class="home_callout"><img class="homeIcon" src="images/home_results.png"><a href="https://testpilot.mozillalabs.com/testcases/"><?php echo _w('All Test Cases &raquo;')?></a></span></div> <br>

				</div>
			
			</div>
			
<div id="footer"><?php echo _w('<img class="mozLogo" src="images/mozilla-logo.png">Copyright &copy; 2005-2009 Mozilla. All rights reserved. &nbsp; &nbsp; <a href="http://labs.mozilla.com/">Mozilla Labs</a> &nbsp; &nbsp; <a href="http://www.mozilla.com/en-US/privacy-policy.html">Privacy Policy</a> &nbsp; &nbsp; <a href="http://www.mozilla.com/en-US/about/legal.html">Legal Notices</a>')?></div>

		
			
		</div>
			
		
</body>
</html>

