using Auth.Application.Interfaces;
using MailKit.Net.Smtp;
using Microsoft.Extensions.Configuration;
using MimeKit;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Services
{
    public class EmailService : IEmailService
    {
        private readonly IConfiguration _configuration;

        public EmailService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public async Task SendPasswordResetEmailAsync(string toEmail, string resetToken, int expiryMinutes)
        {
            var emailSettings = _configuration.GetSection("EmailSettings");

            var message = new MimeMessage();
            message.From.Add(new MailboxAddress(emailSettings["SenderName"], emailSettings["SenderEmail"]));
            message.To.Add(new MailboxAddress("", toEmail));
            message.Subject = "Şifre Sıfırlama Talebi - Interview Asistant";

            var bodyBuilder = new BodyBuilder
            {
                HtmlBody = $@"
<!DOCTYPE html>
<html lang=""tr"">
<body style=""margin:0;padding:0;background-color:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;"">
  <table role=""presentation"" width=""100%"" cellpadding=""0"" cellspacing=""0"" style=""background-color:#f1f5f9;padding:40px 16px;"">
    <tr>
      <td align=""center"">
        <table role=""presentation"" width=""480"" cellpadding=""0"" cellspacing=""0"" style=""background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 12px rgba(15,23,42,0.08);"">

          <tr>
            <td style=""background-color:#4f46e5;padding:28px 32px;"">
              <span style=""color:#ffffff;font-size:20px;font-weight:700;letter-spacing:-0.3px;"">Interview Asistant</span>
            </td>
          </tr>

          <tr>
            <td style=""padding:36px 32px 28px 32px;"">
              <h1 style=""margin:0 0 12px 0;font-size:20px;color:#0f172a;font-weight:700;"">Şifre Sıfırlama Talebi</h1>
              <p style=""margin:0 0 24px 0;font-size:14px;line-height:22px;color:#475569;"">
                Hesabın için bir şifre sıfırlama talebi aldık. Aşağıdaki kodu, şifreni sıfırlama ekranına girerek devam edebilirsin.
              </p>

              <table role=""presentation"" width=""100%"" cellpadding=""0"" cellspacing=""0"">
                <tr>
                  <td align=""center"" style=""background-color:#eef2ff;border:1px solid #c7d2fe;border-radius:12px;padding:20px;"">
                    <span style=""font-family:'Consolas','Courier New',monospace;font-size:32px;font-weight:700;letter-spacing:6px;color:#4338ca;"">
                      {resetToken}
                    </span>
                  </td>
                </tr>
              </table>

              <p style=""margin:20px 0 0 0;font-size:13px;line-height:20px;color:#94a3b8;"">
                Bu kod <strong>{expiryMinutes} dakika</strong> boyunca geçerlidir. Süre dolduktan sonra yeni bir talep oluşturman gerekir.
              </p>
            </td>
          </tr>

          <tr>
            <td style=""padding:0 32px 32px 32px;"">
              <table role=""presentation"" width=""100%"" cellpadding=""0"" cellspacing=""0"" style=""border-top:1px solid #e2e8f0;padding-top:20px;"">
                <tr>
                  <td style=""font-size:12.5px;line-height:19px;color:#94a3b8;"">
                    Bu talebi sen yapmadıysan güvenle görmezden gelebilirsin — hesabında herhangi bir değişiklik yapılmayacak.
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <tr>
            <td style=""background-color:#f8fafc;padding:18px 32px;text-align:center;"">
              <span style=""font-size:11.5px;color:#94a3b8;"">Bu e-posta Interview Asistant Destek tarafından otomatik olarak gönderilmiştir.</span>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>",

                TextBody = $@"Şifre Sıfırlama Talebi - Interview Asistant

Hesabın için bir şifre sıfırlama talebi aldık.
Sıfırlama kodun: {resetToken}

Bu kod {expiryMinutes} dakika boyunca geçerlidir.

Bu talebi sen yapmadıysan bu e-postayı görmezden gelebilirsin."
            };

            message.Body = bodyBuilder.ToMessageBody();

            using var client = new SmtpClient();

            await client.ConnectAsync(emailSettings["SmtpServer"], int.Parse(emailSettings["SmtpPort"]), MailKit.Security.SecureSocketOptions.StartTls);
            await client.AuthenticateAsync(emailSettings["SenderEmail"], emailSettings["Password"]);
            await client.SendAsync(message);
            await client.DisconnectAsync(true);
        }
    }
}
