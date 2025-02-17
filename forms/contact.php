<?php
ob_start();
ini_set('display_errors', 0);
error_reporting(0);
header('Content-Type: text/plain');

// Include the PHP_Email_Form class.
if (file_exists($php_email_form = 'php-email-form.php')) {
  include($php_email_form);
} else {
  die('Unable to load the PHP_Email_Form library!');
}

// Create an instance of the PHP_Email_Form class.
$contact = new PHP_Email_Form;
$contact->ajax = true;
$contact->to = "sdts.mails@gmail.com"; // Set your recipient email address.

// Collect form data.
$contact->from_name  = $_POST['name'];
$contact->from_email = $_POST['email'];
$contact->subject    = $_POST['subject'];

// Build the message using the add_message() method.
$contact->add_message("Name: " . $_POST['name'], "text");
$contact->add_message("Email: " . $_POST['email'], "text");
$contact->add_message("Message: " . $_POST['message'], "text");

// Send the email.
$result = $contact->send();

// Clear any buffered output.
ob_clean();

// Return exactly "success" if the email was sent.
if ($result === "success") {
  http_response_code(200);
  echo "OK";
  exit;
} else {
  echo $result;
  exit;
}