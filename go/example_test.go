package rockware_test

// The README's examples, so a change that breaks them fails to compile.
// They have no Output line, so go test builds them but doesn't run them.

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/rockwarehq/rockware-sdk/go"
)

func Example() {
	ctx := context.Background()
	client, err := rockware.NewClient(rockware.Config{
		Host:      "https://acme-api.rockware.io",
		Token:     os.Getenv("ROCKWARE_TOKEN"),
		UserAgent: "acme-erp-sync/1.0",
	})
	if err != nil {
		log.Fatal(err)
	}

	site, err := client.GetSite(ctx)
	if err != nil {
		log.Fatal(err)
	}
	if site != nil {
		fmt.Println(site.Name)
	}
}

func Example_read() {
	ctx := context.Background()
	client, _ := rockware.NewClient(rockware.Config{Host: "https://acme-api.rockware.io", Token: os.Getenv("ROCKWARE_TOKEN")})

	// One page.
	page, err := client.ListOrders(ctx, &rockware.ListOrdersOptions{First: rockware.Ptr(50)})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(len(page.Nodes))

	// Every record, page by page.
	for product, err := range client.ListAllProducts(ctx, nil) {
		if err != nil {
			log.Fatal(err)
		}
		fmt.Println(product.Sku, product.Name)
	}

	// Only what changed since the last sync.
	since := time.Now().Add(-24 * time.Hour)
	for order, err := range client.ListAllOrders(ctx, &rockware.ListAllOrdersOptions{UpdatedSince: &since}) {
		if err != nil {
			log.Fatal(err)
		}
		since = order.UpdatedAt
	}
}

func Example_send() {
	ctx := context.Background()
	client, _ := rockware.NewClient(rockware.Config{Host: "https://acme-api.rockware.io", Token: os.Getenv("ROCKWARE_TOKEN")})

	result, err := client.UpsertOrder(ctx, rockware.OrderInput{
		ExternalID:  "SO-1001",
		OrderNumber: rockware.Ptr("1001"),
		Customer:    &rockware.CustomerInput{ExternalID: "C-42", Name: "Globex"},
		Lines:       []rockware.OrderLineInput{{Product: "P-100", TargetQuantity: 500}},
	}, nil)
	if err != nil {
		log.Fatal(err)
	}
	if len(result.Errors) > 0 {
		// All or nothing: nothing was saved.
		for _, problem := range result.Errors {
			fmt.Println(problem.Field, problem.Message)
		}
		return
	}
	fmt.Println(*result.Action, result.Order.ID)
}

func Example_errors() {
	ctx := context.Background()
	client, _ := rockware.NewClient(rockware.Config{Host: "https://acme-api.rockware.io", Token: os.Getenv("ROCKWARE_TOKEN")})

	_, err := client.ListProducts(ctx, nil)
	var rwErr *rockware.Error
	if errors.As(err, &rwErr) {
		fmt.Println(rwErr.Code, rwErr.Message, rwErr.Hint, rwErr.RequestID)
	}
}

func Example_webhooks() {
	secret := os.Getenv("ROCKWARE_WEBHOOK_SECRET")
	http.HandleFunc("/rockware", func(w http.ResponseWriter, r *http.Request) {
		body, _ := io.ReadAll(r.Body)
		event, err := rockware.ParseWebhook(secret, body, r.Header.Get(rockware.SignatureHeader), nil)
		if err != nil {
			http.Error(w, "bad signature", http.StatusUnauthorized)
			return
		}
		w.WriteHeader(http.StatusOK) // Answer within 10 seconds, then do the work.
		fmt.Println(event.ID, event.Type, event.Data.Object, event.Data.ID)
	})
}
