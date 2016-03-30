<?php
	if($_POST && isset($_POST['location'], $_POST['service'], $_POST['check'], $_POST['value'])) {
		$redis_server = 'localhost:6379';

		try {
			$redis = new Redis();
			$redis->connect($redis_server);

			$location = $_POST['location'];
			$service = $_POST['service'];
			$check = $_POST['check'];
			$value = $_POST['value'];

			$date = new DateTime();
			$timestamp = $date->getTimestamp();

			$redis->hSet('locations', $location, $timestamp);
			$redis->hSet('services', $service, $timestamp);
			$redis->hSet('checks', $check, $timestamp);

			if ($redis->hExists($location . ':' . $service, $check)) {
				$prev_value = $redis->hGet($location . ':' . $service, $check);
			} else {
				$prev_value = "";
			}

			$redis->hSet($location . ':' . $service, $check, $value);
			if (strcmp($prev_value, "RUN") != 0) {
				$redis->hSet($location . ':' . $service, $check . ':prev', $prev_value);
			}

			$redis->hSet($location . ':' . $service, $check . ':time', $timestamp);
		} catch (RedisException $e) {
			die($e->getMessage());
		}
	}
?>
