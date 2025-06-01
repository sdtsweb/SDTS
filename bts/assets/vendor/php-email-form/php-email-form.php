<?php
/**
 * PHP Email Form
 * Version: 3.10
 * Website: https://bootstrapmade.com/php-email-form/
 * Copyright: BootstrapMade.com
 */

if ( version_compare(phpversion(), '5.5.0', '<') ) {
  die('PHP version 5.5.0 and up is required. Your PHP version is ' . phpversion());
}

class PHP_Email_Form {

  public $to = false;
  public $from_name = false;
  public $from_email = false;
  public $subject = false;
  public $mailer = false;
  public $smtp = false;
  public $message = '';
  public $headers = array(); // Add this line to declare headers property

  public $content_type = 'text/html';
  public $charset = 'utf-8';
  public $ajax = false;

  public $options = [];
  public $cc = [];
  public $bcc = [];
  public $honeypot = '';
  public $recaptcha_secret_key = false;

  public $error_msg = array(
    'invalid_to_email' => 'Email to (receiving email address) is empty or invalid!',
    'invalid_from_name' => 'From Name is empty!',
    'invalid_from_email' => 'Email from: is empty or invalid!',
    'invalid_subject' => 'Subject is too short or empty!',
    'short' => 'is too short or empty!',
    'ajax_error' => 'Sorry, the request should be an Ajax POST',
    'invalid_attachment_extension' => 'File extension not allowed, please choose:',
    'invalid_attachment_size' => 'Max allowed attachment size is:'
  );

  private $error = false;
  private $attachments = [];

  public function __construct() {
    $this->mailer = "forms@" . @preg_replace('/^www\./','', $_SERVER['SERVER_NAME']);
  }

  public function add_message($content, $label = '', $length_check = false) {
    if( $length_check ) {
      if( strlen($content) < $length_check ) {
        $this->error .=  $label . ' ' . $this->error_msg['short'] . '<br>';
        return;
      }
    }
    $content .= '<br>';
    $this->message .= !empty( $label ) ? '<strong>' . $label . ':</strong> ' . $content : $content;
  }

  public function option($name, $val) {
    $this->options[$name] = $val;
  }

  public function add_attachment($name, $max_size = 20, $allowed_exensions = ['jpeg','jpg','png','pdf','doc','docx'] ) {
    if( !empty($_FILES[$name]['name']) ) {
      $file_exension = strtolower(pathinfo($_FILES[$name]['name'], PATHINFO_EXTENSION));
      if( ! in_array($file_exension, $allowed_exensions) ) {
        die( '(' .$name . ') ' . $this->error_msg['invalid_attachment_extension'] . " ." . implode(", .", $allowed_exensions) );
      }
  
      if( $_FILES[$name]['size'] > (1024 * 1024 * $max_size) ) {
        die( '(' .$name . ') ' . $this->error_msg['invalid_attachment_size'] . " $max_size MB");
      }

      $this->attachments[] = [
        'path' => $_FILES[$name]['tmp_name'], 
        'name'=>  $_FILES[$name]['name']
      ];
    }
  }

  public function send() {
    try {
      // Basic validation
      if (empty($this->from_email) || !filter_var($this->from_email, FILTER_VALIDATE_EMAIL)) {
        throw new Exception("Invalid sender email address");
      }

      if (empty($this->to) || !filter_var($this->to, FILTER_VALIDATE_EMAIL)) {
        throw new Exception("Invalid recipient email address");
      }

      // Construct headers string
      $headers = array();
      $headers[] = 'From: ' . $this->from_name . ' <' . $this->from_email . '>';
      $headers[] = 'Reply-To: ' . $this->from_email;
      $headers[] = 'Return-Path: ' . $this->from_email;
      $headers[] = 'MIME-Version: 1.0';
      $headers[] = 'Content-Type: text/plain; charset=UTF-8';
      $headers[] = 'X-Mailer: PHP/' . phpversion();

      $headerStr = implode("\r\n", $headers);

      // Log the email attempt
      error_log("Attempting to send email:");
      error_log("To: " . $this->to);
      error_log("From: " . $this->from_email);
      error_log("Subject: " . $this->subject);
      error_log("Headers: " . $headerStr);

      // Send the email
      if (mail($this->to, $this->subject, $this->message, $headerStr)) {
        return "success";
      } else {
        $error = error_get_last();
        throw new Exception("Mail sending failed: " . ($error['message'] ?? 'Unknown error'));
      }
    } catch (Exception $e) {
      return "Mailer Error: " . $e->getMessage();
    }
  }
}
