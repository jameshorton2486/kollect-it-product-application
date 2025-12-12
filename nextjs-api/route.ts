// /src/app/api/admin/products/service-create/route.ts
// Secure product creation endpoint for desktop app and automation worker
// Authentication: x-api-key header with SERVICE_API_KEY

import { NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { generateSlug } from "@/lib/utils";

// TypeScript interfaces for type safety
interface ProductImage {
  url: string;
  alt: string;
  order: number;
}

interface ProductPayload {
  title: string;
  sku: string;
  category: string;
  subcategory?: string;
  description: string;
  descriptionHtml: string;
  price: number;
  originalPrice?: number;
  condition: string;
  conditionDetails?: string;
  era?: string;
  origin?: string;
  materials?: string[];
  dimensions?: {
    height?: string;
    width?: string;
    depth?: string;
    weight?: string;
  };
  provenance?: string;
  images: ProductImage[];
  seoTitle?: string;
  seoDescription?: string;
  seoKeywords?: string[];
  status?: "draft" | "active" | "sold" | "archived";
  featured?: boolean;
  authentication?: {
    authenticated: boolean;
    method?: string;
    notes?: string;
  };
}

// Validate the API key
function validateApiKey(request: Request): boolean {
  const apiKey = request.headers.get("x-api-key");
  const validKey = process.env.SERVICE_API_KEY;
  
  if (!validKey) {
    console.error("SERVICE_API_KEY not configured in environment");
    return false;
  }
  
  return apiKey === validKey;
}

// Validate required fields in payload
function validatePayload(data: ProductPayload): { valid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  if (!data.title || data.title.trim().length === 0) {
    errors.push("Title is required");
  }
  
  if (!data.sku || data.sku.trim().length === 0) {
    errors.push("SKU is required");
  }
  
  if (!data.category || data.category.trim().length === 0) {
    errors.push("Category is required");
  }
  
  if (!data.description || data.description.trim().length === 0) {
    errors.push("Description is required");
  }
  
  if (typeof data.price !== "number" || data.price < 0) {
    errors.push("Valid price is required");
  }
  
  if (!data.condition || data.condition.trim().length === 0) {
    errors.push("Condition is required");
  }
  
  if (!data.images || !Array.isArray(data.images) || data.images.length === 0) {
    errors.push("At least one image is required");
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

export async function POST(request: Request) {
  // Log request for debugging (remove in production if needed)
  console.log("[service-create] Incoming request");
  
  // Validate API key
  if (!validateApiKey(request)) {
    console.warn("[service-create] Unauthorized request - invalid API key");
    return NextResponse.json(
      { 
        success: false, 
        error: "Unauthorized",
        message: "Invalid or missing API key"
      },
      { status: 401 }
    );
  }
  
  try {
    // Parse request body
    const data: ProductPayload = await request.json();
    
    // Validate payload
    const validation = validatePayload(data);
    if (!validation.valid) {
      return NextResponse.json(
        {
          success: false,
          error: "Validation failed",
          messages: validation.errors
        },
        { status: 400 }
      );
    }
    
    // Check for duplicate SKU
    const existingProduct = await prisma.product.findUnique({
      where: { sku: data.sku }
    });
    
    if (existingProduct) {
      return NextResponse.json(
        {
          success: false,
          error: "Duplicate SKU",
          message: `Product with SKU ${data.sku} already exists`
        },
        { status: 409 }
      );
    }
    
    // Generate URL slug from title
    const slug = generateSlug(data.title);
    
    // Create the product in database
    const product = await prisma.product.create({
      data: {
        title: data.title.trim(),
        slug: slug,
        sku: data.sku.trim().toUpperCase(),
        categoryId: data.category,
        subcategory: data.subcategory || null,
        description: data.description,
        descriptionHtml: data.descriptionHtml,
        price: data.price,
        originalPrice: data.originalPrice || null,
        condition: data.condition,
        conditionDetails: data.conditionDetails || null,
        era: data.era || null,
        origin: data.origin || null,
        materials: data.materials || [],
        dimensions: data.dimensions || {},
        provenance: data.provenance || null,
        seoTitle: data.seoTitle || data.title,
        seoDescription: data.seoDescription || data.description.substring(0, 160),
        seoKeywords: data.seoKeywords || [],
        status: data.status || "draft",
        featured: data.featured || false,
        authentication: data.authentication || { authenticated: false },
        createdAt: new Date(),
        updatedAt: new Date(),
        // Create associated images
        images: {
          create: data.images.map((img, index) => ({
            url: img.url,
            alt: img.alt || `${data.title} - Image ${index + 1}`,
            order: img.order ?? index,
            createdAt: new Date()
          }))
        }
      },
      include: {
        images: true,
        category: true
      }
    });
    
    console.log(`[service-create] Product created: ${product.id} - ${product.sku}`);
    
    // Return success response
    return NextResponse.json({
      success: true,
      product: {
        id: product.id,
        sku: product.sku,
        slug: product.slug,
        title: product.title,
        status: product.status,
        url: `https://kollect-it.com/products/${product.slug}`,
        adminUrl: `https://kollect-it.com/admin/products/${product.id}`,
        imageCount: product.images.length,
        createdAt: product.createdAt
      }
    }, { status: 201 });
    
  } catch (error) {
    console.error("[service-create] Error:", error);
    
    // Handle Prisma errors
    if (error instanceof Error) {
      if (error.message.includes("Unique constraint")) {
        return NextResponse.json(
          {
            success: false,
            error: "Database constraint error",
            message: "A product with this identifier already exists"
          },
          { status: 409 }
        );
      }
    }
    
    return NextResponse.json(
      {
        success: false,
        error: "Internal server error",
        message: "Failed to create product"
      },
      { status: 500 }
    );
  }
}

// GET endpoint to check service status
export async function GET(request: Request) {
  if (!validateApiKey(request)) {
    return NextResponse.json(
      { success: false, error: "Unauthorized" },
      { status: 401 }
    );
  }
  
  return NextResponse.json({
    success: true,
    service: "kollect-it-product-service",
    version: "1.0.0",
    status: "operational",
    timestamp: new Date().toISOString()
  });
}
