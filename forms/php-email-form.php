<?php
/**
 * php-email-form.php
 *
 * A simple class to handle sending contact form emails.
 * This implementation uses PHP’s mail() function.
 * For more robust delivery, consider using an SMTP library.
 */

class PHP_Email_Form {
  public $ajax = false;
  public $to;
  public $from_name;
  public $from_email;
  public $subject;
  public $message = "";
  public $smtp = array(); // Optional SMTP configuration

  /**
   * Adds a message fragment to the email content.
   *
   * @param string $msg The message text to add.
   * @param string $type (Optional) The type of message; defaults to 'text'.
   */
  public function add_message($msg, $type = 'text') {
    // You can customize formatting based on $type if needed.
    $this->message .= $msg . "\n";
  }

  /**
   * Validates that all required fields have been set and are valid.
   *
   * @return bool True if validation passes; false otherwise.
   */
  private function validate() {
    if (empty($this->from_name) || empty($this->from_email) || empty($this->subject) || empty($this->message)) {
      return false;
    }
    if (!filter_var($this->from_email, FILTER_VALIDATE_EMAIL)) {
      return false;
    }
    return true;
  }

  /**
   * Sends the email using PHP's mail() function.
   *
   * @return string "success" if the email was sent; error message otherwise.
   */
  public function send() {
    if (!$this->validate()) {
      return "Validation failed: Please check your input.";
    }
    
    $headers = "From: " . $this->from_name . " <" . $this->from_email . ">";
    
    if (mail($this->to, $this->subject, $this->message, $headers)) {
      return "success";
    } else {
      return "Mail sending failed.";
    }
  }
}
?>