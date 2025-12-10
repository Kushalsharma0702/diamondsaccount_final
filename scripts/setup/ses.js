const nodemailer = require("nodemailer");

async function sendTestMail() {
  let transporter = nodemailer.createTransport({
    host: "email-smtp.ca-central-1.amazonaws.com",
    port: 587,
    auth: {
      user: "AKIA3BMJ25BIYDGPA47X",
      pass: "BDSPNqu7MlgZ38C1yPMEOZ2X43DgvpJYOMc4ddVA1CJl",
    },
  });

  let info = await transporter.sendMail({
    from: "diamondacc.project@gmail.com",
    to: "diamondacc.project@gmail.com",
    subject: "Test OTP",
    text: "Your OTP is 123456",
  });

  console.log("Email sent:", info.messageId);
}

sendTestMail();
