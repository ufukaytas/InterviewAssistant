using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.DTOs
{
    public class GoogleUserProfileDto
    {
        public string Email { get; set; } = null!;
        public string FirstName { get; set; } = null!;
        public string LastName { get; set; } = null!;
    }
}
