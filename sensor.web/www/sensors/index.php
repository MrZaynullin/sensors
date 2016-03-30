<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8"/>
		<title>Sensors Dashboard</title>
		<link rel="stylesheet" href="style.css">
		<script src="jquery.min.js"></script> 
		<script>
			var auto_refresh = setInterval(
			function()
			{
				$('#sensors').load('sensors.php');
			}, 500);
		</script>
	</head>

	<body>
		<div id="dashboard">
			<div id="title" align="center">
			<h1 align="center">Dashboard</h1>
			<?php include ("colors.php"); ?>

			<table style='width: 50%; border: 2px solid black;'>
				<tr>
					<th style='background-color: <?php echo $success; ?>'>Success</th>
					<th style='background-color: <?php echo $run; ?>'>Run</th>
					<th style='background-color: <?php echo $warning; ?>'>Warning</th>
					<th style='background-color: <?php echo $fail; ?>'>Fail</th>
					<th style='background-color: <?php echo $unsupported; ?>'>Unsupported</th>
				</tr>
			</table>
			</div>

			<div id="sensors" align="center"></div>
		</div>
	</body>
</html>
