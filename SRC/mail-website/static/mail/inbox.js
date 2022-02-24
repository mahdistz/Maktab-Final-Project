document.addEventListener(
  "DOMContentLoaded",
  function () {
    const form = document.querySelector("#compose-form");
    const msg = document.querySelector("#message");
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      to = document.querySelector("#compose-recipients");
      subject = document.querySelector("#compose-subject");
      body = document.querySelector("#compose-body");
      if (from.length == 0 && to.length == 0) return;

      fetch("/emails", {
        method: "POST",
        body: JSON.stringify({
          recipients: to.value,
          subject: subject.value,
          body: body.value,
        }),
      })
        .then((response) => response.json())
        .then((result) => {
          console.log(result.status);
          if (result.status == 201) {
            load_mailbox("sent");
          } else {
            msg.innerHTML = `<div class="alert alert-danger" role="alert">
            ${result.error}
          </div>`;
          }
        });
    });
  },
  false
);

document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"));
  document.querySelector("#is_sent").addEventListener("click", () => load_mailbox("sent"));
  document.querySelector("#is_archived").addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Clear out composition fields
  document.querySelector("#compose-recipients").value = "";
  document.querySelector("#compose-subject").value = "";
  document.querySelector("#compose-body").value = "";
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#compose-view").style.display = "none";

  // Show the mailbox name
  document.querySelector("#emails-view").innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  if (mailbox == "show_mail") {
    show_mail();
    return;
  }

  fetch(`/emails/${mailbox}`)
    .then((response) => response.json())
    .then((emails) => {
      emails.forEach((element) => {
        if (mailbox != "sent") {
          sender_recipients = element.sender;
        } else {
          sender_recipients = element.recipients;
        }
        if (mailbox == "inbox") {
          if (element.read) is_read = "is_read";
          else is_read = "";
        }
        var item = document.createElement("div");
        item.className = `card ${is_read} my-1 items`;

        item.innerHTML = `<div style="border: 1px solid black; height: 35px;" id="item-${element.id}">
        
        <strong style="font-size: 14pt;">&nbsp;${sender_recipients}</strong>&nbsp;&nbsp;&nbsp; ${element.subject} <div style="float: right; font-weight: 150">${element.created_time}</div>
        
        <br>
      </div>`;
        document.querySelector("#emails-view").appendChild(item);
        item.addEventListener("click", () => {
          show_mail(element.id, mailbox);
        });
      });
    });
}

function show_mail(id, mailbox) {
  fetch(`/emails/${id}`)
    .then((response) => response.json())
    .then((email) => {
      // Print email
      // console.log(email);
      document.querySelector("#emails-view").innerHTML = "";
      var item = document.createElement("div");
      item.innerHTML = `<div style="white-space: pre-wrap;">
  <strong>From:</strong> ${email.sender}
  <strong>To:</strong> ${email.recipients}
  <strong>Subject:</strong> ${email.subject}
  <strong>Created Time:</strong> ${email.created_time}
  </div>
  `;
      document.querySelector("#emails-view").appendChild(item);
      if (mailbox == "sent") return;
      let archive = document.createElement("btn");
      archive.className = `btn btn-outline-primary my-2`;
      archive.addEventListener("click", () => {
        toggle_archive(id, email.archived);
        if (archive.innerText == "Archive") archive.innerText = "Unarchive";
        else archive.innerText = "Archive";
      });
      if (!email.archived) archive.textContent = "Archive";
      else archive.textContent = "Unarchive";
      document.querySelector("#emails-view").appendChild(archive);

      let reply = document.createElement("btn");
      reply.className = `btn btn-outline-primary m-2`;
      reply.textContent = "Reply";
      reply.addEventListener("click", () => {
        reply_mail(email.sender, email.subject, email.body, email.created_time);
      });
      document.querySelector("#emails-view").appendChild(reply);
      make_read(id);
      let hr = document.createElement("HR");
      document.querySelector("#emails-view").appendChild(hr);
      let message = document.createElement("div");
      message.innerHTML = `${email.body}`;
      document.querySelector("#emails-view").appendChild(message);
    });
}

function toggle_archive(id, state) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: !state,
    }),
  });
}

function make_read(id) {
  fetch(`/emails/${id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });
}

function reply_mail(sender, subject, body, created_time) {
  compose_email();
  if (!/^Re:/.test(subject)) subject = `Re: ${subject}`;
  document.querySelector("#compose-recipients").value = sender;
  document.querySelector("#compose-subject").value = subject;

  pre_fill = `On ${created_time} ${sender} wrote:\n${body}\n`;

  document.querySelector("#compose-body").value = pre_fill;
}