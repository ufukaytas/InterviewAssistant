using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Text;
using System.Threading.RateLimiting;
using Yarp.ReverseProxy.Transforms;

var builder = WebApplication.CreateBuilder(args);

// JWT
var jwtSettings = builder.Configuration.GetSection("JwtSettings");
var secretKey = jwtSettings["Key"];
if (string.IsNullOrWhiteSpace(secretKey))
    throw new InvalidOperationException(
        "JwtSettings:Key tanımlı değil (appsettings.Development.json ya da JwtSettings__Key env).");

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.MapInboundClaims = false; // "sub" claim'i olduğu gibi kalsın
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = jwtSettings["Issuer"],
            ValidateAudience = true,
            ValidAudience = jwtSettings["Audience"],
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
            ValidateLifetime = true
        };
    });

//builder.Services.AddAuthorization(options =>
//{
//    options.AddPolicy("default", policy => policy.RequireAuthenticatedUser());
//});

builder.Services.AddAuthorization();

// CORS (origin'ler appsettings'ten)
var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>();
if (allowedOrigins is null || allowedOrigins.Length == 0)
    throw new InvalidOperationException(
        "Cors:AllowedOrigins tanımlı değil");

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowReactUI", policy => policy
        .WithOrigins(allowedOrigins)
        .AllowAnyHeader()
        .AllowAnyMethod());
});

// Rate limiting
builder.Services.AddRateLimiter(options =>
{
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;

    // Auth route'ları: brute-force koruması, IP başına
    options.AddPolicy("auth-limit", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.Connection.RemoteIpAddress?.ToString() ?? "unknown",
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 10,
                Window = TimeSpan.FromMinutes(1),
                QueueLimit = 0
            }));

    // Diğer route'lar: kullanıcı başına (sub), yoksa IP
    options.AddPolicy("api-limit", context =>
        RateLimitPartition.GetFixedWindowLimiter(
            context.User.FindFirst("sub")?.Value
                ?? context.Connection.RemoteIpAddress?.ToString()
                ?? "unknown",
            _ => new FixedWindowRateLimiterOptions
            {
                PermitLimit = 100,
                Window = TimeSpan.FromMinutes(1),
                QueueLimit = 0
            }));
});

// YARP + X-User-Id transform
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"))
    .AddTransforms(builderContext =>
    {
        builderContext.AddRequestTransform(transformContext =>
        {
            // Client'ın kendi gönderdiği X-User-Id'yi asla iletme (spoofing)
            transformContext.ProxyRequest.Headers.Remove("X-User-Id");

            if (transformContext.HttpContext.User.Identity?.IsAuthenticated == true)
            {
                var userId = transformContext.HttpContext.User
                    .FindFirst(JwtRegisteredClaimNames.Sub)?.Value;

                if (!string.IsNullOrEmpty(userId))
                    transformContext.ProxyRequest.Headers.Add("X-User-Id", userId);
            }
            return ValueTask.CompletedTask;
        });
    });

builder.Services.AddHealthChecks();

var app = builder.Build();

app.UseRouting();
app.UseCors("AllowReactUI");
app.UseAuthentication();
app.UseAuthorization();
app.UseRateLimiter(); // routing + auth'tan sonra: route politikası ve sub okunabilir

app.MapHealthChecks("/health");
app.MapReverseProxy();

app.Run();