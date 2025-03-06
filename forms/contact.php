<?php
// Include PHPMailer classes manually
require_once '../vendor/PHPMailer/src/Exception.php';
require_once '../vendor/PHPMailer/src/PHPMailer.php';
require_once '../vendor/PHPMailer/src/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Set up error logging
ini_set('log_errors', 1);
ini_set('error_log', __DIR__ . '/error.log');
error_reporting(E_ALL);

header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

// Debug logging
error_log("POST data received: " . print_r($_POST, true));

try {
    $mail = new PHPMailer(true);

    //Server settings
    $mail->isSMTP();
    $mail->Host       = 'smtp.gmail.com';  // Gmail SMTP server
    $mail->SMTPAuth   = true;
    $mail->Username   = 'your-email@gmail.com'; // Your Gmail
    $mail->Password   = 'your-app-password';    // Your Gmail App Password
    $mail->SMTPSecure = 'tls';
    $mail->Port       = 587;

    //Recipients
    $mail->setFrom($_POST['email'], $_POST['name']);
    $mail->addAddress('sdts.mails@gmail.com');
    $mail->addReplyTo($_POST['email'], $_POST['name']);

    //Content
    $mail->isHTML(true);
    $mail->Subject = $_POST['subject'];
    $mail->Body    = "Name: {$_POST['name']}<br>Email: {$_POST['email']}<br><br>Message:<br>{$_POST['message']}";
    $mail->AltBody = strip_tags($mail->Body);

    $mail->send();
    error_log("Email sent successfully");
    echo "OK";

} catch (Exception $e) {
    error_log("Mailer Error: " . $mail->ErrorInfo);
    http_response_code(500);
    echo "Error: " . $mail->ErrorInfo;
}
?>