using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Domain.Entities
{
    public class RefreshToken : BaseEntity
    {
        public string Token { get; set; } = null!;
        public string? AccessToken { get; set; }
        public DateTime ExpiresDate { get; set; }
        public bool IsExpired => DateTime.UtcNow >= ExpiresDate;
        public DateTime? RevokedDate { get; set; } // logout
        public bool IsActiveToken => RevokedDate == null && !IsExpired;
        public Guid UserId { get; set; }
        public User User { get; set; } = null!;
    }
}
