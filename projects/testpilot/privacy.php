<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
	<?php require_once('../../hooks/php/pontoon.php'); ?>
	<?php Pontoon::header_tags('testpilot', 'index', 'pontoon.json');?>
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
			
					<span class="menuItem"><a href="index.php"><?php echo _w('Home')?></a></span>

					<span class="menuItem"><a href="testcases.php"><?php echo _w('Test Cases')?></a></span>
					<span class="menuItem"><a href="principles.php"><?php echo _w('Guiding Principles')?></a></span>
                    <span class="menuItem"><a href="faq.php"><?php echo _w('FAQ')?></a></span>
					<span class="menuOn"><a href="privacy.php"><?php echo _w('Privacy Policy')?></a></span>

				
				</div>
				
				<div id="intro">

				
					<h2><?php echo _w('Privacy Policy')?></h2>
			  
					<p><?php echo _w('Test Pilot is a platform collecting structured user feedback through Firefox. Test Pilot studies explore how people use their web browser and the Internet - and help us build better products. ')?></p>
				  
				         <p><?php echo _w('As a Test pilot, not only will you try before anyone else the newest features and coolest user-interface ideas, you could also learn how those study results may contribute to future designs. The goal for this platform is to encourage everyone from all skill levels to improve the Web experience by conducting and participating in these studies.')?></p>

<p><?php echo _w('Once you <a href="https://addons.mozilla.org/services/install.php?addon_id=testpilot"> install the Test Pilot add-on</a>, you will automatically  receive notifications on upcoming and finished studies. You have the full control on your participation: ')?></p>
				  <ul><li><?php echo _w('You choose if you want to participate in a particular study')?></li>

				    <li><?php echo _w('You can see what data has been collected from you in real time ')?></li>
				    <li><?php echo _w('At the end of a study, you choose if you want to submit your data to the Test Pilot servers')?></li>
				    <li><?php echo _w('You also have the option to quit the platform')?></li>
				    <li><?php echo _w('If the test requires you to install a new feature or product, the platform will ask for your permission')?></li></ul>

				    <p><?php echo _w('Test Pilot study results are made available under open licenses, with the data being anonymized before release.')?></p>

<p><?php echo _w('When a product is not easy to use, don\'t just wonder why it\'s designed that way. Make your mark on the design and help us improve it! <a href="https://addons.mozilla.org/services/install.php?addon_id="testpilot"> Join the forces, we want you! </a>')?></p>

 <div class="home_button"><a href="https://testpilot.mozillalabs.com/faq.html"><?php echo _w('Learn more about Test Pilot &raquo;')?></a></div>
				</div>
				
				<div id="links">
				
					<div class="home_callout"><img class="homeIcon" src="images/home_computer.png"> <a href="http://labs.mozilla.com/projects/test-pilot/"><?php echo _w('Test Pilot Blog &raquo;')?></a></div> <br>
					
					<div class="home_callout"><img class="homeIcon" src="images/home_upcoming.png"><a href="https://wiki.mozilla.org/Labs/Test_Pilot"><?php echo _w('Test Pilot Wiki &raquo;')?></a></div> <br>
					
					<div class="home_callout"><img class="homeIcon" src="images/home_results.png"><a href="https://testpilot.mozillalabs.com/testcases/"><?php echo _w('All Test Cases &raquo;')?></a></span></div> <br>

				</div>
			
			</div>
			
<div id="footer"><img class="mozLogo" src="images/mozilla-logo.png"><?php echo _w('Copyright &copy; 2005-2009 Mozilla. All rights reserved. &nbsp; &nbsp; <a href="http://labs.mozilla.com/">Mozilla Labs</a> &nbsp; &nbsp; <a href="http://www.mozilla.com/en-US/privacy-policy.html">Privacy Policy</a> &nbsp; &nbsp; <a href="http://www.mozilla.com/en-US/about/legal.html">Legal Notices</a>')?></div>

		
			
		</div>
			
		
	<?php Pontoon::footer_tags();?>		
</body>
</html>

