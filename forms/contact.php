<?php
ob_start();
ini_set('display_errors', 1);
error_reporting(E_ALL);
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

// Debug information
error_log("POST data received: " . print_r($_POST, true));
error_log("PHP loaded .ini file: " . php_ini_loaded_file());
error_log("PHP Sendmail Path: " . ini_get('sendmail_path'));
error_log("PHP SMTP settings: " . ini_get('SMTP') . ":" . ini_get('smtp_port'));

try {
    // First validate the email
    if (empty($_POST['email']) || !filter_var($_POST['email'], FILTER_VALIDATE_EMAIL)) {
        throw new Exception('Invalid email address provided');
    }

    // Include the PHP_Email_Form class
    if (file_exists($php_email_form = '../assets/vendor/php-email-form/php-email-form.php')) {
        include($php_email_form);
    } else {
        throw new Exception('Unable to load the PHP_Email_Form library!');
    }

    $contact = new PHP_Email_Form;
    
    // Set the required properties
    $contact->to = 'sdts.mails@gmail.com';
    $contact->from_email = $_POST['email'];
    $contact->from_name = $_POST['name'] ?? 'Website Visitor';
    $contact->subject = $_POST['subject'] ?? 'New Contact Form Message';
    
    // Build message content
    $messageContent = "From: " . $_POST['name'] . "\n";
    $messageContent .= "Email: " . $_POST['email'] . "\n\n";
    $messageContent .= "Message:\n" . $_POST['message'];
    
    $contact->add_message($messageContent);
    
    // Send and handle response
    $result = $contact->send();
    
    ob_clean();
    
    if ($result === "success") {
        http_response_code(200);
        echo "OK";
    } else {
        throw new Exception($result);
    }

} catch (Exception $e) {
    ob_clean();
    error_log("Contact form error: " . $e->getMessage());
    error_log("Stack trace: " . $e->getTraceAsString());
    http_response_code(500);
    echo "Error: " . $e->getMessage();
}
?>