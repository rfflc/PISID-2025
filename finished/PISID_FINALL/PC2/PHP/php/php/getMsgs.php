<?php
	$db = "pisid"; //database name
	$username = $_POST["username"];
	$password = $_POST["password"];
	$dbhost = "localhost"; 

    $conn = mysqli_connect($dbhost,$username,$password,$db);
	$sql = "SELECT mensagem, leitura, sala, sensor, tipo, hora, hora_escrita from mensagens where Hora >= now() - interval 60 minute ORDER BY Hora DESC";
	$response["mensagens"] = array();
	$result = mysqli_query($conn, $sql);	
	if ($result){
		if (mysqli_num_rows($result)>0){		
			while($r=mysqli_fetch_assoc($result)){	
				try {	
					$ad = array();
					$ad["Msg"] = $r['mensagem'];				
					$ad["leitura"] = $r['leitura'];
					$ad["Sala"] = $r['sala'];
					$ad["Sensor"] = $r['sensor'];				
					$ad["TipoAlerta"] = $r['tipo'];
					$ad["Hora"] = $r['hora'];
					$ad["HoraEscrita"] = $r['hora_escrita'];
				array_push($response["mensagens"], $ad);			
				}
				catch (Exception $e) {echo ($e);}
			}
		}
	}
	header('Content-Type: application/json');
	// tell browser that its a json data
	echo json_encode($response);
	//converting array to JSON string
?>