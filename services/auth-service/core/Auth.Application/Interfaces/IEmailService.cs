using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IEmailService
    {
        Task SendPasswordResetEmailAsync(string toEmail, string resetToken, int expiryMinutes);
    }
}
