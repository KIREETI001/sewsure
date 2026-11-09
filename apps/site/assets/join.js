// Waitlist and tailor sign-up forms.
// Sign-ups are not open yet: this script does not send, store or log what is typed.
// When a backend is connected (needs-human: see apps/site/README.md), replace the
// message branch below with a request to the API. Never send to a public sheet.
(function () {
  var MESSAGE = "Sign-ups are not open yet. Nothing you typed has been sent or saved.";

  var forms = document.querySelectorAll("form[data-form]");

  forms.forEach(function (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var message = form.querySelector(".form-message");
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }

      message.textContent = MESSAGE;
      form.reset();
    });
  });
})();
