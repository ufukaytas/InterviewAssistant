using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Domain.Entities
{
    public class Role : BaseEntity
    {
        public string RoleName { get; set; } = null!;

        public ICollection<UserRole> UserRoles { get; set; } = new List<UserRole>();
    }
}
