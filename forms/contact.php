<?php
ob_start();
ini_set('display_errors', 1);
error_reporting(E_ALL);
header('Content-Type: text/plain');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type, X-Requested-With');

error_log("POST data received: " . print_r($_POST, true));

try {
    // Include the PHP_Email_Form class.
    if (file_exists($php_email_form = __DIR__ . '/php-email-form.php')) {
        include($php_email_form);
    } else {
        throw new Exception('Unable to load the PHP_Email_Form library!');
    }

    // Validate POST data
    if (empty($_POST['name']) || empty($_POST['email']) || empty($_POST['subject']) || empty($_POST['message'])) {
        throw new Exception('All fields are required');
    }

    // Create an instance of the PHP_Email_Form class.
    $contact = new PHP_Email_Form;
    $contact->ajax = true;
    $contact->to = "sdts.mails@gmail.com";

    // Add additional headers for better email delivery
    $contact->headers = array(
        'MIME-Version: 1.0',
        'Content-type: text/html; charset=UTF-8',
        'X-Mailer: PHP/' . phpversion()
    );

    // Collect form data.
    $contact->from_name = filter_var($_POST['name'], FILTER_SANITIZE_STRING);
    $contact->from_email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
    $contact->subject = filter_var($_POST['subject'], FILTER_SANITIZE_STRING);

    // Build the message
    $contact->add_message("From: " . $contact->from_name, "text");
    $contact->add_message("Email: " . $contact->from_email, "text");
    $contact->add_message("Message: " . $_POST['message'], "text");

    // Send the email.
    $result = $contact->send();

    // Clear any buffered output.
    ob_clean();

    // Return response
    if ($result === "success") {
        http_response_code(200);
        echo "OK";
    } else {
        throw new Exception($result);
    }

} catch (Exception $e) {
    ob_clean();
    http_response_code(500);
    echo "Error: " . $e->getMessage();
}
?>