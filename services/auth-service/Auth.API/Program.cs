using Auth.API.Middlewares;
using Auth.Application;
using Auth.Application.Interfaces;
using Auth.Application.Mappings;
using Auth.Domain.Entities;
using Auth.Infrastructure;
using Auth.Infrastructure.Contexts;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.

builder.Services.AddControllers();

// swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(x =>
{
    x.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "InterviewAsistant",
        Version = "v1"
    });
    x.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "Enter Jwt Bearer Token"
    });
    x.AddSecurityRequirement(document =>
                    new OpenApiSecurityRequirement
                    {
                        [new OpenApiSecuritySchemeReference("Bearer", document)] = []
                    });
});

//application serviceRegister
builder.Services.AddApplicationServices();

// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

builder.Services.AddInfrastructure(builder.Configuration);
builder.Services.AddAutoMapper(cfg => cfg.AddMaps(typeof(RegisterProfile).Assembly));

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["JwtSettings:Issuer"],
            ValidAudience = builder.Configuration["JwtSettings:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration["JwtSettings:Key"]!))

        };
    });
builder.Services.AddAuthorization();

var app = builder.Build();

//global exception middleware
app.UseMiddleware<GlobalExceptionMiddleware>();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwagger();
    app.UseSwaggerUI();
}

//app.UseHttpsRedirection();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

using (var scope = app.Services.CreateScope())
{
    var services = scope.ServiceProvider;
    try
    {
        var dbContext = services.GetRequiredService<AuthDbContext>();
        var passwordHasher = services.GetRequiredService<IPasswordHasher>();
        // Veritabanı yoksa oluşturur ve bekleyen tüm migration'ları uygular
        dbContext.Database.Migrate();

        var testEmail = "test@gmail.com";
        if (!dbContext.Users.Any(u => u.Email == testEmail))
        {
            var testUser = new User
            {
                Id = Guid.NewGuid(),
                FirstName = "Test_User",
                LastName = "Candidate",
                Email = testEmail,
                PasswordHash = passwordHasher.Hash("Password123"),
                CreatedDate = DateTime.UtcNow
            };
            dbContext.Users.Add(testUser);
            dbContext.SaveChanges();
        }
    }
    catch (Exception ex)
    {
        var logger = services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "Veritabanına seed data eklenirken bir hata oluştu.");
    }
}

app.Run();
