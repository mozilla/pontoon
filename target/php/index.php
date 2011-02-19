<?php
header('Content-type: text/html; charset=utf-8');
if (array_key_exists('lang', $_GET))
  $locale = $_GET['lang'];
else
  $locale = 'en-US';
putenv("LC_ALL=".$locale);
setlocale(LC_ALL,$locale);
bindtextdomain('messages','./locale');
textdomain('messages');

require_once('./pontoon.php');

?>
<html>
<head>
<?php Pontoon::header_tags();?>
<script type="text/javascript">
function f() {
	  var w = "<?php echo _w("My name is <span>Gandalf</span>"); ?>"
	  $('#foo').html(w);
	  $('#foo > span').text('foo2');
	}

</script>
</head>
<body>
<span id="foo"></span>
<h1><?php echo _w('This is a title'); ?></h1>
<hr/>
<h2><?php echo _w('The list of locales we have'); ?></h2>
<ul>
  <li><a href="./">en-US</a></li>
<?php
foreach (new DirectoryIterator('./locale') as $fileInfo) {
    if($fileInfo->isDot()) continue;
    echo '<li><a href="?lang='.$fileInfo->getFilename().'">'.$fileInfo->getFilename() . "</a></li>";
}
?>
</ul>
<script type="text/javascript" src="/client/www/js/jquery-1.4.2-min.js"></script>
<script type="text/javascript">
f();
</script>
</body>
</html>
