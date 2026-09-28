using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Domain.Entities
{
    public abstract class BaseEntity
    {
        public Guid Id { get; set; }
        public DateTime CreatedDate { get; set; }
        public DateTime? UpdatedDate { get; set; }
        public bool IsActive { get; set; } = true;
        public bool? IsDeleted { get; set; } = false; // Soft delete için
    }
}
