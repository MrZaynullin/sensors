<?php
	$redis_server = 'localhost:6379';

	try {
		$redis = new Redis();
		$redis->connect($redis_server);

		$locations = $redis->hKeys('locations');
		$services = $redis->hKeys('services');
		$checks = $redis->hKeys('checks');
		sort($locations);
		sort($services);
		sort($checks);

		$tbl = "<table><tr><th></th>";

		foreach ($locations as $location) {
			$tbl .= "<th>" . $location . "</th>";
		}

		$tbl .= "</tr>";

		$date = new DateTime();
		$timestamp = $date->getTimestamp();
		$rowscount = count($checks);

		foreach ($services as $service) {
			$nonexist_locations = array();

			$service_row = "<tr><td rowspan=%d style='border-top-style: solid;'>" . $service . "</td>";
			$opentag = 0;
			$closetag = 1;

			foreach ($checks as $check) {
				$add_check = 1;

				foreach ($locations as $location) {
					$value = $redis->hGet($location . ':' . $service, $check);
					$prev_value = $redis->hGet($location . ':' . $service, $check . ':prev');

					$is_supported = False;

					if ($redis->hExists($location . ':' . $service, $check . ':time')) {
						if ($add_check == 1 && $opentag == 1) {
							$service_row .= "<tr>";
							$add_check = 0;
							$closetag = 1;
						}

						$time = $redis->hGet($location . ':' . $service, $check . ':time');
						if ($timestamp - $time < 60) {
							$is_supported = True;
						} else {
							$is_supported = False;
						}

						$service_row = choose_cell_color($service_row, $check, $value, $prev_value, $opentag, $is_supported);
					} else {
						array_push($nonexist_locations, $check);
					}
				}

				if ($closetag == 1) {
					$service_row .= "</tr>";
					$opentag = 1;
				}
			}

			$service_row .= "</tr>";
			$service_row = sprintf($service_row, $rowscount - sizeof(array_unique($nonexist_locations)));
			$tbl .= $service_row;
		}

		$tbl .= "</table>";

		echo $tbl;
	} catch(RedisException $e) {
		die($e->getMessage());
	}

	function choose_cell_color($tbl, $check, $value, $prev_value, $opentag, $is_supported) {
		include "colors.php";

		if (!$is_supported){
			$value = "NONE";
		}

		switch ($value) {
			case "OK":
				$color = $success;
				break;
			case "RUN":
				switch ($prev_value) {
					case "OK":
						$color = "linear-gradient(to left, " . $run . " 0%%, " . $success . " 100%%)";
						break;
					case "FAIL":
						$color = "linear-gradient(to left, " . $run . " 0%%, " . $fail . " 100%%)";
						break;
					case "WARN":
						$color = "linear-gradient(to left, " . $run . " 0%%, " . $warning . " 100%%)";
						break;
					default:
						$color = $run;
				}

				break;
			case "WARN":
				$color = $warning;
				break;
			case "FAIL":
				$color = $fail;
				break;
			case "NONE":
				$color = $unsupported;
				break;
			default:
				$color = $default;
		}

		if ($opentag == 1) {
			$tbl .= "<td style='border-top-style: hidden; background: " . $color . ";'>" . $check . "</td>";
		} else {
			$tbl .= "<td style='background: " . $color . ";'>" . $check . "</td>";
		}

		return $tbl;
	}
?>
